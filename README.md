# DCP Custom Blender Worker

Leveraging custom worktimes and the custom-worker base class, we are able to develop a custom blender worktime which enables users to safely render job deployers' scenes without executing untrusted code on their local machine. 


## Getting Started

To get started, simply run the following:

1. `pip install -r ./requirements.txt`
2. `uvicorn dcp_custom_blender_worker.main:app --port 8001`
3. `npm run start`
4. ???
5. Profit 💰💰💰
