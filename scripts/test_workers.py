import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.workers import QueueManager
from app.workers import ScanWorker, AnalysisWorker, ExportWorker, CleanupWorker
from app.userbot import UserbotManager

async def test_queue():
    print("Testing QueueManager...")
    
    queue = QueueManager()
    await queue.connect()
    
    test_job = {
        "type": "test",
        "data": "test_data"
    }
    
    job_id = await queue.push(test_job)
    print(f"Job pushed: {job_id}")
    
    length = await queue.get_queue_length()
    print(f"Queue length: {length}")
    
    popped = await queue.pop()
    print(f"Popped job: {popped}")
    
    await queue.clear()
    await queue.disconnect()
    
    print("QueueManager test passed")

async def test_workers():
    print("\nTesting Workers...")
    
    queue = QueueManager()
    await queue.connect()
    
    userbot_manager = UserbotManager()
    
    scan_worker = ScanWorker(queue, userbot_manager)
    analysis_worker = AnalysisWorker(queue)
    export_worker = ExportWorker(queue)
    cleanup_worker = CleanupWorker(queue)
    
    await scan_worker.start()
    await analysis_worker.start()
    await export_worker.start()
    await cleanup_worker.start()
    
    print(f"Scan worker running: {scan_worker.is_running()}")
    print(f"Analysis worker running: {analysis_worker.is_running()}")
    print(f"Export worker running: {export_worker.is_running()}")
    print(f"Cleanup worker running: {cleanup_worker.is_running()}")
    
    await scan_worker.stop()
    await analysis_worker.stop()
    await export_worker.stop()
    await cleanup_worker.stop()
    
    await queue.disconnect()
    
    print("Workers test passed")

async def test_job_flow():
    print("\nTesting Job Flow...")
    
    queue = QueueManager()
    await queue.connect()
    
    job_data = {
        "type": "test_scan",
        "user_id": 1,
        "source_id": 1
    }
    
    job_id = await queue.push(job_data)
    print(f"Job pushed: {job_id}")
    
    await queue.update_status(job_id, "running", progress=50)
    status = await queue.get_status(job_id)
    print(f"Job status: {status}")
    
    await queue.update_status(job_id, "completed", progress=100)
    status = await queue.get_status(job_id)
    print(f"Job status after completion: {status}")
    
    await queue.clear()
    await queue.disconnect()
    
    print("Job flow test passed")

async def main():
    print("=== Workers Component Tests ===\n")
    
    await test_queue()
    await test_workers()
    await test_job_flow()
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(main())