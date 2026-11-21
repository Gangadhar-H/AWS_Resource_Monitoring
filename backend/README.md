# Cloud Cost Monitor - Backend (MVP)

Read-only scanner that finds idle/underutilised cloud resources (AWS first), estimates
their monthly cost and potential savings, and serves results to a dashboard.

## Run
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # then fill in read-only AWS keys
uvicorn app.main:app --reload                          # http://localhost:8000/docs
pytest                                                 # tests use mocked AWS, no account needed
```

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | /api/scan | Run a fresh scan, store and return it |
| GET | /api/resources?type=&status= | Flagged resources from latest scan |
| GET | /api/summary | Totals from latest scan |
| GET | /api/inventory?type=&status=&q= | Every resource from the latest scan (flagged or healthy) |
| GET | /api/inventory/{type}/{id} | Full details of one resource |
| POST | /api/inventory/{type}/{id}/scan | Re-check one resource, returns fresh details and savings |
| GET | /api/scans | Scan history |
| GET | /api/health | Health check |

## Rules
1. EC2 running >= 14 days with average CPU < 5%  -> `underutilized`
2. EC2 stopped with attached EBS volumes         -> `stopped`
3. EBS volume in `available` state               -> `unused`
4. Elastic IP with no association                -> `unused`

Costs come from hardcoded assumptions in `app/cost/pricing.py` (verify before reporting).
The scanner never modifies or deletes anything. Minimum IAM permissions:
`ec2:DescribeInstances`, `ec2:DescribeVolumes`, `ec2:DescribeAddresses`, `cloudwatch:GetMetricStatistics`.
