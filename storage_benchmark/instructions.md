### Instructions to Collect Storage Benchmark Results

## Step 1
Run storage.sh on Atlas HPC

```bash
sbatch storage.sh
```

## Step 2
The current test is for the `/scratch` directory. To run the test for `/data` and the local NFS (`/home`), change the `TARGET_DIR` parameter in `storage.sh`

## Step 3
Using the results obtained in the log file, generate the table for sequential and random R/W operations across all three types of storage featured by Atlas HPC.
