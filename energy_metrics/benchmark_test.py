#!/usr/bin/env python3
import os
import time
import argparse
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import torchvision.transforms as transforms
import torchvision.models as models
from transformers import BertForSequenceClassification, BertTokenizerFast

class RealDiskImageDataset(Dataset):
    """Reads large realistic uncompressed image payloads from disk to pressure I/O."""
    def __init__(self, root_dir, num_samples=5000):
        self.root_dir = root_dir
        os.makedirs(root_dir, exist_ok=True)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])
        
        self.filepaths = [os.path.join(root_dir, f"img_{i:06d}.raw") for i in range(num_samples)]
        
        # Populate files if missing (1024x1024 raw RGB ~ 3 MB per image => ~15 GB dataset)
        missing = [p for p in self.filepaths if not os.path.exists(p)]
        if missing:
            print(f"[*] Generating {len(missing)} uncompressed high-res payloads in {root_dir}...")
            for path in missing:
                # Random bytes to defeat compression/caching tricks
                data = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)
                with open(path, "wb") as f:
                    f.write(data.tobytes())

    def __len__(self):
        return len(self.filepaths)

    def __getitem__(self, idx):
        path = self.filepaths[idx]
        with open(path, "rb") as f:
            raw_bytes = f.read()
        
        arr = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((512, 512, 3))
        img = Image.fromarray(arr)
        tensor = self.transform(img)
        label = idx % 1000
        return tensor, torch.tensor(label, dtype=torch.long)


class RealDiskTextDataset(Dataset):
    """Reads distinct text files directly from disk per sample."""
    def __init__(self, root_dir, num_samples=5000, seq_len=128):
        self.root_dir = root_dir
        self.seq_len = seq_len
        self.txt_dir = os.path.join(root_dir, "txt_shards")
        os.makedirs(self.txt_dir, exist_ok=True)
        self.tokenizer = BertTokenizerFast.from_pretrained("bert-base-uncased")

        self.filepaths = [os.path.join(self.txt_dir, f"doc_{i:06d}.txt") for i in range(num_samples)]
        missing = [p for p in self.filepaths if not os.path.exists(p)]
        if missing:
            print(f"[*] Generating {len(missing)} text files in {self.txt_dir}...")
            for i, path in enumerate(missing):
                with open(path, "w") as f:
                    f.write(f"Sample sequence document {i} analyzing multi-tenant HPC storage contention and DRBD replication latency across nodes.\n" * 15)

    def __len__(self):
        return len(self.filepaths)

    def __getitem__(self, idx):
        path = self.filepaths[idx]
        with open(path, "r") as f:
            text = f.read()
        
        encoding = self.tokenizer(
            text,
            max_length=self.seq_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        return encoding["input_ids"].squeeze(0), encoding["attention_mask"].squeeze(0), torch.tensor(idx % 2, dtype=torch.long)


def get_model(model_name, device):
    if model_name == "resnet50":
        model = models.resnet50()
        loss_fn = nn.CrossEntropyLoss()
    elif model_name == "vit_b_16":
        model = models.vit_b_16()
        loss_fn = nn.CrossEntropyLoss()
    elif model_name == "bert_base":
        model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
        loss_fn = None
    return model.to(device), loss_fn


def run_benchmark(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, loss_fn = get_model(args.model, device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

    if args.model in ["resnet50", "vit_b_16"]:
        dataset = RealDiskImageDataset(args.data_dir, num_samples=args.dataset_size)
    else:
        dataset = RealDiskTextDataset(args.data_dir, num_samples=args.dataset_size)

    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=args.workers,
        pin_memory=True,
        shuffle=True,
        drop_last=True
    )

    # Checkpoint write directory on the active tier
    ckpt_dir = os.path.join(args.data_dir, "checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)

    model.train()

    # Warmup iterations
    for i, batch in enumerate(loader):
        if i >= 3:
            break
        if args.model == "bert_base":
            ids, mask, y = [b.to(device, non_blocking=True) for b in batch]
            loss = model(ids, attention_mask=mask, labels=y).loss
        else:
            x, y = batch[0].to(device, non_blocking=True), batch[1].to(device, non_blocking=True)
            loss = loss_fn(model(x), y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

    if torch.cuda.is_available():
        torch.cuda.synchronize()

    # Timed Measurement Loop
    total_samples = 0
    t_wait_total = 0.0
    epoch_start = time.perf_counter()

    batch_end_time = time.perf_counter()
    for step, batch in enumerate(loader):
        batch_ready_time = time.perf_counter()
        t_wait_total += (batch_ready_time - batch_end_time)

        optimizer.zero_grad()
        if args.model == "bert_base":
            ids, mask, y = [b.to(device, non_blocking=True) for b in batch]
            bsz = ids.size(0)
            loss = model(ids, attention_mask=mask, labels=y).loss
        else:
            x, y = batch[0].to(device, non_blocking=True), batch[1].to(device, non_blocking=True)
            bsz = x.size(0)
            loss = loss_fn(model(x), y)

        loss.backward()
        optimizer.step()

        # Emulate regular micro-checkpointing every 25 steps to stress write bandwidth/IOPS
        if step % 25 == 0:
            ckpt_path = os.path.join(ckpt_dir, f"step_{step}.pt")
            torch.save(model.state_dict(), ckpt_path)

        if torch.cuda.is_available():
            torch.cuda.synchronize()

        total_samples += bsz
        batch_end_time = time.perf_counter()

    epoch_end = time.perf_counter()
    t_total = epoch_end - epoch_start
    throughput = total_samples / t_total
    delta_io = (t_wait_total / t_total) * 100.0

    print(f"\n[{args.tier}] {args.model} Results:")
    print(f"  T_epoch: {t_total:.2f} s | delta_I/O: {delta_io:.2f} % | Throughput: {throughput:.1f} smp/s")
    print(f"SUMMARY_ROW: {args.tier} | {args.model} | {t_total:.2f} | {delta_io:.2f} | {throughput:.1f}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True, choices=["resnet50", "vit_b_16", "bert_base"])
    parser.add_argument("--tier", type=str, required=True, help="Storage tier label")
    parser.add_argument("--data-dir", type=str, required=True, help="Path to read dataset files from")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--dataset-size", type=int, default=5000)
    args = parser.parse_args()
    run_benchmark(args)