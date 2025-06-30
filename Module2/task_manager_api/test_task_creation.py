import asyncio
import httpx
from datetime import datetime

async def test_task_api():
    base_url = "http://localhost:8000"
    
    # Test user credentials
    username = f"testuser_{datetime.now().timestamp()}"
    password = "testpass123"
    
    async with httpx.AsyncClient() as client:
        # 1. Register a new user
        print("1. Registering new user...")
        register_response = await client.post(
            f"{base_url}/auth/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": password
            }
        )
        print(f"Register response: {register_response.status_code}")
        if register_response.status_code != 200:
            print(f"Register error: {register_response.text}")
            return
        
        # 2. Login to get token
        print("\n2. Logging in...")
        login_response = await client.post(
            f"{base_url}/auth/login",
            data={
                "username": username,
                "password": password
            }
        )
        print(f"Login response: {login_response.status_code}")
        if login_response.status_code != 200:
            print(f"Login error: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create a task
        print("\n3. Creating a task...")
        create_task_response = await client.post(
            f"{base_url}/tasks/",
            headers=headers,
            json={
                "title": "Test Task",
                "description": "This is a test task to verify fetch_link"
            }
        )
        print(f"Create task response: {create_task_response.status_code}")
        if create_task_response.status_code != 200:
            print(f"Create task error: {create_task_response.text}")
            return
        
        task_data = create_task_response.json()
        print(f"Created task: {task_data}")
        print(f"Owner data type: {type(task_data.get('owner'))}")
        print(f"Owner data: {task_data.get('owner')}")
        
        # 4. Get all tasks
        print("\n4. Getting all tasks...")
        get_tasks_response = await client.get(
            f"{base_url}/tasks/",
            headers=headers
        )
        print(f"Get tasks response: {get_tasks_response.status_code}")
        if get_tasks_response.status_code == 200:
            tasks = get_tasks_response.json()
            print(f"Number of tasks: {len(tasks)}")
            if tasks:
                print(f"First task owner: {tasks[0].get('owner')}")
        
        # 5. Get specific task
        if 'id' in task_data:
            print(f"\n5. Getting specific task {task_data['id']}...")
            get_task_response = await client.get(
                f"{base_url}/tasks/{task_data['id']}",
                headers=headers
            )
            print(f"Get task response: {get_task_response.status_code}")
            if get_task_response.status_code == 200:
                single_task = get_task_response.json()
                print(f"Task owner: {single_task.get('owner')}")
        
        # 6. Update task
        if 'id' in task_data:
            print(f"\n6. Updating task {task_data['id']}...")
            update_response = await client.put(
                f"{base_url}/tasks/{task_data['id']}",
                headers=headers,
                json={
                    "title": "Updated Test Task",
                    "completed": True
                }
            )
            print(f"Update task response: {update_response.status_code}")
            if update_response.status_code == 200:
                updated_task = update_response.json()
                print(f"Updated task: {updated_task}")
                print(f"Updated task owner: {updated_task.get('owner')}")

if __name__ == "__main__":
    asyncio.run(test_task_api())