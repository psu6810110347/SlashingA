## ภาพรวมของโปรแกรม (Program Overview)
เกม SlashingA เป็นเกมแนว Hack and Slash 2D ที่พัฒนาด้วย Kivy Framework (Python) หน้าที่ของผู้เล่นคือควบคุมตัวละครเพื่อต่อสู้ เอาชีวิตรอดจากศัตรูที่จะคอยเดินเข้ามาโจมตี โดยระหว่างทางผู้เล่นสามารถเดินเก็บ Perk (ลูกแก้วพลังงานสีต่างๆ) เพื่อช่วยเพิ่มค่าสถานะของตัวละคร (พลังชีวิต, พลังโจมตี, การป้องกัน, และความเร็ว) ให้แข็งแกร่งขึ้นเพื่อให้สามารถจัดการศัตรูที่เก่งขึ้นตามเวลาได้

## การติดตั้งและการรันโปรแกรม (Installation & Execution)
1. **ตรวจสอบ Python**: เครื่องของท่านจำเป็นต้องติดตั้ง Python ไว้
2. **ติดตั้ง Kivy**: เกมนี้พัฒนาด้วย Kivy สามารถติดตั้ง library ได้ด้วยคำสั่ง:
   ```bash
   pip install kivy
   ```
3. **การรันเกม**: เปิด Terminal / Command Prompt นำทางไปยังโฟลเดอร์ของเกมและรันคำสั่ง:
   ```bash
   python main.py
   ```

**การควบคุม (Controls):**
- **W, A, S, D**: เคลื่อนที่ (Move)
- **คลิกเมาส์ซ้าย (Left Click)**: โจมตีศัตรู (Attack)
- **P**: หยุดเกมชั่วคราว (Pause)
- **ESC**: กลับสู่หน้าเมนูหลัก (Main Menu)

## อธิบายการทำงานของโค้ด (Code Architecture & Workflow)
โครงสร้างโปรแกรมถูกแบ่งเป็นหลายส่วนทำงานร่วมกัน (Modular structure) เพื่อให้ง่ายต่อการดูแลจัดการดังนี้:

- **`main.py`**
  ไฟล์หลัก (Entry Point) สำหรับเปิดโปรแกรม ทำหน้าที่สร้าง `HackAndSlashApp` จัดการ `ScreenManager` เพื่อสลับการแสดงผลระหว่างเมนูเกมและหน้าเกม รับ Input จากคีย์บอร์ดและเมาส์ และเป็น Game Loop หลัก (ด้วยความเร็วอัปเดตที่ 60 FPS) สำหรับควบคุมการขยับของตัวละคร, วาดกราฟิกตัวละคร/ศัตรู/Perk ต่างๆ ลงบน Canvas และจัดการระบบชน (Collision) เมื่อผู้เล่นเดินไปเก็บ Perk

- **`ui/widgets.py`**
  รับผิดชอบการสร้างและวาด User Interface (UI) ต่างๆ ให้กับเกมโดยต่อยอดจากเครื่องมือของ Kivy เช่น `MainMenuScreen` (หน้าจอก่อนเริ่มเกม), `GameScreen` (หน้าจอรวม HUD, แผงสถานะผู้เล่นด้านซ้าย และพื้นที่วาดเกม) ตลอดจน `PauseMenuPopup`

- **`game/` (Game Logic Sub-module)**
  จัดการเนื้อหาลอจิกภายในเกมผ่าน `game_manager.py` เช่น การสุ่มเกิดของศัตรูและแพทเทิร์นการปรับสเกลค่าพลังของศัตรูตามเวลา (Scaling), ตัวจับเวลาของเกม (Timer), จัดการการเกิดของ Perk, และเก็บข้อมูลสถานะผู้เล่น

- **`events/callbacks.py`**
  ตัวจัดการเหตุการณ์เมื่อมีการกดปุ่มหรือกระทำต่างๆ เพื่อแยกส่วน Logic ให้ออกจากส่วนแสดงผล เช่น เมื่อกดปุ่ม Start เกม, ปุ่ม Pause หรือกดโจมตี (Attack) ตัว Callback จะอัปเดต State หรือแจ้งให้ Game Manager ทราบต่อไป


# SlashingA - Game Design Document

## Player Stats
- **Max HP**: 100
- **Attack Damage**: 5
- **Movement Speed**: 5
- **Health Regen**: Regenerates normally over time

## Enemy Types & Scaling
*All enemies must constantly walk toward the player.*

### Normal
- **Base HP**: 10 (+10 every 5 minutes)
- **Base Speed**: 4
- **Base Damage**: 10 (+5 every 5 minutes)

### Tank
- **Base HP**: 20 (+10 every 5 minutes)
- **Base Speed**: 3
- **Base Damage**: 10 (+5 every 5 minutes)

### Shooter
- **Base HP**: 10 (+10 every 5 minutes)
- **Base Speed**: 4
- **Base Damage**: 10 (+5 every 5 minutes)
- **Special**: Can shoot projectiles at the player

## Perks (Power-ups)
*Perks spawn randomly every 1 minute. The player can choose which to collect.*

### Attack Boost
- Increases Player Damage by 1

### Health Boost
- Increases Player Max Health by 10

### Speed Boost
- Increases Player Movement Speed by 1


