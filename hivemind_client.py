"""
╔══════════════════════════════════════════════════════════════════╗
║         HiveMind Client Node — المايسترو (الأوتوماتيكي)         ║
║     (Auto-Decomposer, Parallel Broadcaster & Paymaster)          ║
╠══════════════════════════════════════════════════════════════════╣
║ يكسر المشاريع، يوزعها على السرب في نفس اللحظة، ويحاسب الألفا.    ║
╚══════════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import os
import sys
import uuid

try:
    import websockets
except ImportError:
    print("❌ الرجاء تثبيت المكتبة: pip install websockets")
    sys.exit(1)

DEFAULT_ALPHA_SERVER = "ws://127.0.0.1:8000/alpha"
CONFIG_FILE = "hivemind_client_wallet.json"

class HiveMindClient:
    def __init__(self):
        self.client_id = None
        self.alpha_url = os.environ.get("HIVEMIND_SERVER", DEFAULT_ALPHA_SERVER)
        self.known_workers = [] # قائمة العمال المتاحين في السرب
        
    async def init_wallet(self):
        """فتح حساب للعميل ليتمكن من الدفع للعمال والألفا"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                self.client_id = json.load(f).get("client_id")
                print(f"💼 محفظة العميل جاهزة. هويتك: {self.client_id}")
                return

        print("📡 جاري فتح حساب عميل جديد في البنك المركزي (الألفا)...")
        try:
            async with websockets.connect(self.alpha_url) as ws:
                welcome = json.loads(await ws.recv())
                self.client_id = welcome.get("node_id")
                with open(CONFIG_FILE, "w") as f:
                    json.dump({"client_id": self.client_id}, f)
                print(f"🎉 تم إنشاء الحساب! رصيدك الافتتاحي جاهز لدفع أجور السرب.")
        except Exception as e:
            print(f"❌ لا يمكن الاتصال بالألفا: {e}")
            sys.exit(1)

    def decompose_project(self, project_prompt: str, workers_count: int) -> list:
        """محرك التفكيك: يكسر المشروع الكبير إلى مهام صغيرة بحسب عدد العمال"""
        print(f"🧠 جاري تفكيك المشروع إلى {workers_count} مهام متوازية...")
        # في النسخة الحقيقية، نستخدم LLM لتفكيك الطلب بذكاء، هنا سنقوم بتقسيمه محاكاةً
        tasks = []
        for i in range(workers_count):
            tasks.append(f"الجزء رقم {i+1} من مشروع: {project_prompt}")
        return tasks

    async def send_task_to_worker(self, port: int, task_prompt: str):
        """إرسال المهمة لعامل واحد واستلام النتيجة"""
        try:
            reader, writer = await asyncio.open_connection('127.0.0.1', port)
            task_msg = {
                "action": "GOSSIP_TASK_BROADCAST",
                "prompt": task_prompt,
                "required_role": "any",
                "project_id": uuid.uuid4().hex
            }
            writer.write(json.dumps(task_msg).encode() + b'\n')
            await writer.drain()
            
            # استلام الكود الجاهز
            data = await reader.readline()
            writer.close()
            await writer.wait_closed()
            
            if data:
                response = json.loads(data.decode())
                if response.get("action") == "TASK_COMPLETED":
                    return {"worker_id": response.get("worker_id"), "result": response.get("result")}
        except Exception as e:
            print(f"⚠️ العامل على البورت {port} لا يستجيب.")
            return None

    async def execute_swarm_project(self, project_prompt: str):
        """المايسترو: يوزع المهام على كل العمال في نفس اللحظة (Parallel Execution)"""
        workers_count = len(self.known_workers)
        if workers_count == 0:
            print("❌ لا يوجد عمال في السرب حالياً!")
            return

        print(f"\n🚀 [بث السرب] إطلاق المشروع لـ {workers_count} عمال في نفس اللحظة!")
        
        # 1. تفكيك المشروع
        sub_tasks = self.decompose_project(project_prompt, workers_count)
        
        # 2. إطلاق المهام بالتوازي (سحر الـ P2P)
        coroutines = []
        for i, port in enumerate(self.known_workers):
            coroutines.append(self.send_task_to_worker(port, sub_tasks[i]))
        
        # انتظار جميع العمال لينهوا عملهم معاً
        print("⏳ جاري انتظار إنجاز السرب...")
        results = await asyncio.gather(*coroutines)
        
        # 3. تجميع النتائج والعمال المشاركين
        successful_workers = []
        print("\n==================================================")
        print("✅ [المنتج النهائي المجمع من السرب]:")
        for res in results:
            if res:
                successful_workers.append(res["worker_id"])
                print(f"-> {res['result']}")
        print("==================================================\n")
        
        # 4. دفع الأموال أوتوماتيكياً (بما في ذلك حصة المؤسس)
        if successful_workers:
            await self.pay_workers(successful_workers, project_cost=10.0)

    async def pay_workers(self, workers_used: list, project_cost: float):
        """الاتصال بالألفا لمرة واحدة لتسجيل العقد المالي واقتطاع نسبة الـ 5%"""
        print(f"💸 جاري إرسال {project_cost} IQ للبنك المركزي لتوزيعها على العمال واقتطاع حصة المؤسس...")
        try:
            async with websockets.connect(self.alpha_url) as ws:
                await ws.recv() # تجاوز الترحيب
                payment_msg = {
                    "action": "FINALIZE_AND_PAY",
                    "payload": {
                        "workers_used": workers_used,
                        "project_cost": project_cost
                    }
                }
                await ws.send(json.dumps(payment_msg))
                receipt = json.loads(await ws.recv())
                print(f"🧾 [إيصال البنك]: {receipt.get('message')}")
        except Exception as e:
            print(f"❌ خطأ في الاتصال بالبنك: {e}")

    async def start_cli(self):
        await self.init_wallet()
        print("\n👑 HiveMind Client (المايسترو)")
        
        # اكتشاف العمال المتاحين (في بيئة الاختبار ندخل البورتات مرة واحدة)
        ports_input = input("👉 أدخل بورتات العمال الشغالين مفصولة بفاصلة (مثال: 54321, 54322): ")
        self.known_workers = [int(p.strip()) for p in ports_input.split(",") if p.strip().isdigit()]
        
        print(f"🐝 تم ربط المايسترو بـ {len(self.known_workers)} عمال. السرب جاهز للأوامر!\n")
        
        while True:
            prompt = input("📝 صِف مشروعك الضخم للسرب (أو exit): ")
            if prompt.lower() == 'exit': break
            await self.execute_swarm_project(prompt)

if __name__ == "__main__":
    client = HiveMindClient()
    asyncio.run(client.start_cli())
