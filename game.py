import warnings

# 忽略所有libpng警告
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)

import tkinter as tk
from PIL import Image, ImageTk
import pygame
import time
import json
import os

# 尝试导入音效库
try:
    import pygame
    # 初始化pygame
    # 尝试初始化pygame，捕获可能的错误
    try:
        pygame.init()
        sound_available = True
        #尝试初始化mixer，并捕获可能的错误
        try:
            print("开始初始化pygame.mixer")
            # 使用与测试脚本相同的初始化参数
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("pygame.mixer初始化成功")
            # 测试声音系统是否真的可用
            if pygame.mixer.get_init():
                print(f"Mixer信息: {pygame.mixer.get_init()}")
            else:
                print("Mixer初始化但未返回信息")
        except Exception as e:
            sound_available = False
            print(f"pygame.mixer初始化失败: {e}")
    except Exception as e:
        sound_available = False
        print(f"pygame初始化失败: {e}")
except ImportError as e:
    sound_available = False
    print(f"导入pygame失败: {e}")
except Exception as e:
    sound_available = False
    print(f"其他错误: {e}")

print(f"声音可用状态: {sound_available}")

# 数据存储文件
DATA_FILE = "player_data.json"

# 全局变量
current_window = None
player_name = ""
cricket_name = ""
selected_side = ""
difficulty = "普通"  # 默认难度：简单、普通、困难
window_x = 100  # 窗口X坐标
window_y = 100  # 窗口Y坐标


power = 0  # 蓄力值
power_max = 10  # 蓄力上限
power_label = None  # 蓄力条标签

# 生命值
player_health = 10
enemy_health = 10
player_health_label = None
enemy_health_label = None

# 技能冷却时间
skill1_cooldown = 0
skill2_cooldown = 0
ult_cooldown = 0

# 蛐蛐位置
cricket1_x = 150
cricket1_y = 200
cricket2_x = 450
cricket2_y = 200

# 回合制相关
current_turn = "player"  # 当前回合：player或ai
turn_label = None  # 显示当前回合的标签

# AI相关
ai_last_skill = None  # AI最近使用的技能
ai_turn_in_progress = False  # AI决策是否正在进行中

# 保存玩家数据
def save_player_data(name):
    """保存玩家数据到JSON文件"""
    data = {
        "last_login": name
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已保存玩家数据: {name}")

# 加载玩家数据
def load_player_data():
    """从JSON文件加载玩家数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("last_login", "")
        except Exception as e:
            print(f"加载玩家数据失败: {e}")
            return ""
    return ""

# 清除玩家数据（登出）
def clear_player_data():
    """清除玩家数据"""
    if os.path.exists(DATA_FILE):
        try:
            os.remove(DATA_FILE)
            print("已清除玩家数据")
        except Exception as e:
            print(f"清除玩家数据失败: {e}")

# 加载图片并去除白色背景
def load_image(image_path, size=(150, 150)):
    try:
        image = Image.open(image_path)
        image = image.resize(size, Image.LANCZOS)
        
        # 转换为RGBA模式以支持透明度
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # 获取图片数据
        data = image.getdata()
        new_data = []
        
        # 遍历每个像素，将白色及接近白色的像素设为透明
        for item in data:
            # 如果像素接近白色（R, G, B值都很高），设置为透明
            if item[0] > 200 and item[1] > 200 and item[2] > 200:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        
        # 更新图片数据
        image.putdata(new_data)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"加载图片失败: {e}")
        return None

# 加载原始图片（不进行白色背景去除）
def load_original_image(image_path, size=(150, 150)):
    try:
        image = Image.open(image_path)
        image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"加载图片失败: {e}")
        return None

# 加载背景图片并去除水印
def load_background(image_path, window_size=(600, 400)):
    try:
        image = Image.open(image_path)
        
        # 去除右下角水印（裁剪掉图片底部和右侧的部分区域）
        width, height = image.size
        new_width = int(width * 0.85)  # 保留左侧85%
        new_height = int(height * 0.9)  # 保留顶部90%
        image = image.crop((0, 0, new_width, new_height))
        
        # 调整图片大小以适应窗口，保持宽高比
        image = image.resize(window_size, Image.LANCZOS)
        
        return ImageTk.PhotoImage(image), window_size[0], window_size[1]
    except Exception as e:
        print(f"加载背景失败: {e}")
        return None, 600, 400

# 加载技能图片
def load_skill_images():
    # 左侧蛐蛐技能
    skill1 = load_original_image("技能1.jpg", (50, 50))
    skill2 = load_original_image("技能2.jpg", (50, 50))
    ult1 = load_original_image("大招1.jpg", (50, 50))
    
    # 右侧蛐蛐技能
    skill3 = load_original_image("技能3.jpg", (50, 50))
    skill4 = load_original_image("技能4.jpg", (50, 50))
    ult2 = load_original_image("大招2.jpg", (50, 50))
    
    return (skill1, skill2, ult1), (skill3, skill4, ult2)

# 更新蓄力条
def update_power(root):
    global power, power_label, skill1_cooldown, skill2_cooldown, ult_cooldown, difficulty
    
    # 根据难度调整蓄力获取速度
    power_gain = 1
    if difficulty == "困难":
        power_gain = 1.5
    
    # 每1.5秒恢复蓄力
    if power < power_max:
        power += power_gain
        # 确保蓄力值不超过最大值
        if power > power_max:
            power = power_max
        print(f"蓄力值: {power}")  # 调试信息
    
    # 更新蓄力条显示
    if power_label:
        # 显示数字蓄力值
        power_label.config(text=f"{int(power)}/{power_max}")
        print(f"蓄力条显示: {int(power)}/{power_max}")  # 调试信息
    
    # 减少冷却时间
    if skill1_cooldown > 0:
        skill1_cooldown -= 1.5
    if skill2_cooldown > 0:
        skill2_cooldown -= 1.5
    if ult_cooldown > 0:
        ult_cooldown -= 1.5
    
    # 1.5秒后再次调用
    root.after(1500, lambda: update_power(root))

# 播放音效
def play_sound(sound_file):
    print(f"尝试播放音效: {sound_file}")
    print(f"声音可用状态: {sound_available}")
    
    # 检查文件是否存在
    if not os.path.exists(sound_file):
        print(f"错误: 音效文件不存在: {sound_file}")
        return
    
    if sound_available:
        try:
            # 停止当前可能正在播放的音乐
            pygame.mixer.music.stop()
            # 加载并播放音效
            pygame.mixer.music.load(sound_file)
            print(f"成功加载音效: {sound_file}")
            pygame.mixer.music.play()
            print(f"开始播放音效: {sound_file}")
        except Exception as e:
            print(f"播放音效失败: {e}")
    else:
        print("声音不可用，无法播放音效")

# AI决策函数
def ai_make_decision(root, canvas, cricket_id, start_x, start_y, ai_power, ai_health, player_health):
    """AI根据游戏状态做出决策并使用技能"""
    global difficulty, skill1_cooldown, skill2_cooldown, ult_cooldown, power, current_turn, ai_last_skill, ai_turn_in_progress
    
    # 检查是否有可用技能
    def has_available_skill():
        # 检查技能1或3是否可用
        if ai_power >= 1 and skill1_cooldown <= 0:
            return True
        # 检查技能2是否可用
        if ai_power >= 2 and skill2_cooldown <= 0:
            return True
        # 检查技能4是否可用
        if ai_power >= 3 and ult_cooldown <= 0:
            return True
        return False
    
    # 检查技能是否可用
    def is_skill_available(skill):
        if skill == 1 or skill == 3:
            return ai_power >= 1 and skill1_cooldown <= 0
        elif skill == 2:
            return ai_power >= 2 and skill2_cooldown <= 0
        elif skill == 4:
            return ai_power >= 3 and ult_cooldown <= 0
        return False
    
    # 记录AI最近使用的技能
    import random
    
    # 基于规则的AI决策
    def rule_based_ai():
        global ai_last_skill
        # 收集所有可用技能
        available_skills = []
        if is_skill_available(1):
            available_skills.append(1)
        if is_skill_available(2):
            available_skills.append(2)
        if is_skill_available(3):
            available_skills.append(3)
        if is_skill_available(4):
            available_skills.append(4)
        
        # 根据难度和游戏状态做出决策
        if difficulty == "简单":
            # 简单难度：保守策略
            if ai_health < 3 and is_skill_available(2):
                return 2  # 加血
            elif available_skills:
                # 随机选择可用技能，避免重复使用相同的技能
                if ai_last_skill and len(available_skills) > 1:
                    # 尝试选择与上次不同的技能
                    available_skills = [skill for skill in available_skills if skill != ai_last_skill]
                    if not available_skills:
                        available_skills = [1, 3] if is_skill_available(1) or is_skill_available(3) else [1]
                return random.choice(available_skills)
            else:
                # 没有可用技能，返回1
                return 1
        elif difficulty == "普通":
            # 普通难度：平衡策略
            if ai_health < 4 and is_skill_available(2):
                return 2  # 加血
            elif available_skills:
                # 随机选择可用技能，避免重复使用相同的技能
                if ai_last_skill and len(available_skills) > 1:
                    # 尝试选择与上次不同的技能
                    available_skills = [skill for skill in available_skills if skill != ai_last_skill]
                    if not available_skills:
                        available_skills = [1, 3] if is_skill_available(1) or is_skill_available(3) else [1]
                return random.choice(available_skills)
            else:
                # 没有可用技能，返回1
                return 1
        else:  # 困难
            # 困难难度：激进策略
            if ai_health < 5 and is_skill_available(2):
                return 2  # 加血
            elif available_skills:
                # 随机选择可用技能，避免重复使用相同的技能
                if ai_last_skill and len(available_skills) > 1:
                    # 尝试选择与上次不同的技能
                    available_skills = [skill for skill in available_skills if skill != ai_last_skill]
                    if not available_skills:
                        available_skills = [1, 3] if is_skill_available(1) or is_skill_available(3) else [1]
                return random.choice(available_skills)
            else:
                # 没有可用技能，返回1
                return 1
    
    # 标记AI决策开始
    ai_turn_in_progress = True
    print(f"AI决策开始，标记设置为: {ai_turn_in_progress}")
    
    # 只有当有可用技能时才执行
    if has_available_skill():
        # 尝试使用技能，直到找到可用的技能
        max_attempts = 3  # 尝试多次，确保找到可用的技能
        skill_used = False
        for attempt in range(max_attempts):
            skill_number = rule_based_ai()
            print(f"基于规则的AI选择了技能: {skill_number}")
            
            # 检查技能是否可用
            if is_skill_available(skill_number):
                # 记录AI使用的技能
                ai_last_skill = skill_number
                print(f"AI使用了技能: {skill_number}")
                
                # 根据选择的技能执行相应操作
                if skill_number == 1:
                    use_skill1(root, canvas, cricket_id, start_x, start_y, is_player=False, skill_type=1)
                    skill_used = True
                    return
                elif skill_number == 2:
                    use_skill2(root, is_player=False)
                    skill_used = True
                    return
                elif skill_number == 3:
                    use_skill1(root, canvas, cricket_id, start_x, start_y, is_player=False, skill_type=3)
                    skill_used = True
                    return
                elif skill_number == 4:
                    use_ult(root, canvas, cricket_id, start_x, start_y, is_player=False)
                    skill_used = True
                    return
            else:
                print(f"技能 {skill_number} 不可用，尝试其他技能")
        
        # 兜底方案：尝试使用技能1
        if ai_power >= 1 and skill1_cooldown <= 0:
            print("所有技能都不可用，使用技能1")
            use_skill1(root, canvas, cricket_id, start_x, start_y, is_player=False, skill_type=1)
            skill_used = True
        else:
            # 没有可用技能，直接切换到玩家回合
            print("AI没有可用技能，切换到玩家回合")
            current_turn = "player"
            turn_label.config(text="当前回合: 玩家")
            # 标记AI决策结束
            ai_turn_in_progress = False
            print(f"AI决策结束，标记重置为: {ai_turn_in_progress}")
    else:
        # 没有可用技能，直接切换到玩家回合
        print("AI没有可用技能，切换到玩家回合")
        current_turn = "player"
        turn_label.config(text="当前回合: 玩家")
        # 标记AI决策结束
        ai_turn_in_progress = False
        print(f"AI决策结束，标记重置为: {ai_turn_in_progress}")

# 播放GIF动画
def play_gif(canvas, gif_path, x, y, size=(100, 100), duration=1000):
    try:
        # 打开GIF文件
        gif = Image.open(gif_path)
        frames = []
        
        # 提取所有帧
        try:
            while True:
                # 调整帧大小
                frame = gif.resize(size, Image.LANCZOS)
                frames.append(ImageTk.PhotoImage(frame))
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        
        if not frames:
            print(f"GIF文件 {gif_path} 没有帧")
            return
        
        print(f"成功加载GIF文件 {gif_path}，共 {len(frames)} 帧")
        
        # 创建动画
        frame_ids = []
        animation_running = True
        
        def animate(frame_idx):
            nonlocal animation_running
            if animation_running and frame_idx < len(frames):
                # 清除之前的帧
                for fid in frame_ids:
                    try:
                        canvas.delete(fid)
                    except:
                        pass
                frame_ids.clear()
                
                # 显示当前帧
                fid = canvas.create_image(x, y, image=frames[frame_idx])
                frame_ids.append(fid)
                
                # 继续下一帧
                canvas.after(100, animate, (frame_idx + 1) % len(frames))
        
        # 开始动画
        animate(0)
        
        # 一段时间后停止动画
        def stop_animation():
            nonlocal animation_running
            animation_running = False
            for fid in frame_ids:
                try:
                    canvas.delete(fid)
                except:
                    pass
            frame_ids.clear()
            print(f"GIF动画 {gif_path} 播放结束")
        
        canvas.after(duration, stop_animation)
        
        # 保持对帧的引用，防止被垃圾回收
        canvas.gif_frames = frames
            
    except Exception as e:
        print(f"播放GIF失败: {e}")

# 显示胜利动画
def show_win_animation(root, canvas, is_win):
    if is_win:
        print("显示胜利动画")
        # 清除画布上的所有内容
        canvas.delete("all")
        
        # 显示背景
        background_image = load_image("舞台1.jpg", (600, 400))
        canvas.create_image(300, 200, image=background_image)
        
        # 显示"You win!"文字动画
        win_text = canvas.create_text(300, 150, text="You win!", font=('Arial', 48, 'bold'), fill="red")
    else:
        print("显示失败动画")
        # 清除画布上的所有内容
        canvas.delete("all")
        
        # 显示背景
        background_image = load_image("舞台1.jpg", (600, 400))
        canvas.create_image(300, 200, image=background_image)
        
        # 显示"You Lost!"文字动画
        win_text = canvas.create_text(300, 150, text="You Lost!", font=('Arial', 48, 'bold'), fill="red")
    
    # 动画效果
    def animate_text():
        for i in range(10):
            scale = 1 + i * 0.1
            canvas.scale(win_text, 300, 150, scale, scale)
            canvas.update()
            time.sleep(0.1)
        for i in range(10):
            scale = 2 - i * 0.1
            canvas.scale(win_text, 300, 150, scale, scale)
            canvas.update()
            time.sleep(0.1)
    
    animate_text()
    
    # 创建按钮框架
    button_frame = tk.Frame(root, bg="lightgreen", bd=2, relief="solid")
    button_frame.place(x=150, y=250, width=300, height=80)
    
    # 返回主菜单按钮
    def back_to_menu():
        root.destroy()
        # 确保返回到真正的开始游戏主菜单
        start_menu()
    
    menu_button = tk.Button(
        button_frame, 
        text="返回主菜单", 
        font=('Arial', 14), 
        width=12, 
        height=2, 
        command=back_to_menu
    )
    menu_button.pack(side=tk.LEFT, padx=15, pady=10)
    
    # 再来一局按钮
    def play_again():
        global current_window
        # 先将current_window设置为None，避免在game_window中尝试销毁已销毁的窗口
        current_window = None
        root.destroy()
        game_window()
    
    again_button = tk.Button(
        button_frame, 
        text="再来一局", 
        font=('Arial', 14), 
        width=12, 
        height=2, 
        command=play_again
    )
    again_button.pack(side=tk.RIGHT, padx=15, pady=10)
    
    # 保持对背景图片的引用
    canvas.bg_img = background_image

# 移动蛐蛐
def move_cricket(canvas, cricket_id, start_x, start_y, end_x, end_y, callback=None):
    # 计算移动步数
    steps = 20
    dx = (end_x - start_x) / steps
    dy = (end_y - start_y) / steps
    
    def animate(step):
        if step < steps:
            new_x = start_x + dx * step
            new_y = start_y + dy * step
            canvas.coords(cricket_id, new_x, new_y)
            canvas.after(50, animate, step + 1)
        else:
            canvas.coords(cricket_id, end_x, end_y)
            if callback:
                callback()
    
    animate(0)

# 攻击技能
def attack_skill(root, canvas, cricket_id, start_x, start_y, is_player=True):
    global power, player_health, enemy_health
    
    # 消耗蓄力
    if is_player:
        if selected_side == "left":
            # 调整移动距离，使其更大
            target_x = start_x + 200  # 移动200像素
        else:
            # 调整移动距离，使其更大
            target_x = start_x - 200  # 移动200像素
        
        # 移动到对方位置
        move_cricket(canvas, cricket_id, start_x, start_y, target_x, start_y, lambda:
            # 攻击后返回
            (time.sleep(1), move_cricket(canvas, cricket_id, target_x, start_y, start_x, start_y)))
        
        # 扣除对方生命值
        if selected_side == "left":
            enemy_health -= 2
            if enemy_health < 0:
                enemy_health = 0
            enemy_health_label.config(text=f"对手: {enemy_health}")
        else:
            player_health -= 2
            if player_health < 0:
                player_health = 0
            player_health_label.config(text=f"玩家: {player_health}")
    
    # 播放音效
    play_sound("给我擦皮鞋.mp3")

# 技能1和3（攻击技能）
def use_skill1(root, canvas, cricket_id, start_x, start_y, is_player=True, skill_type=1):
    global power, skill1_cooldown, player_health, enemy_health, player_health_label, enemy_health_label, current_turn, turn_label
    
    print(f"use_skill1 called with skill_type: {skill_type}, is_player: {is_player}")
    print(f"Power: {power}, Cooldown: {skill1_cooldown}")
    print(f"Current turn: {current_turn}")
    
    # 检查回合和蓄力冷却（仅对玩家）
    if is_player and current_turn != "player":
        print("不是玩家回合，无法使用技能")
        return
    
    if not is_player and current_turn != "ai":
        print("不是AI回合，无法使用技能")
        return
    
    # 检查蓄力和冷却
    if power >= 1 and skill1_cooldown <= 0:
        # 播放音效
        print("Playing sound")
        play_sound("给我擦皮鞋.mp3")
        
        # 扣除蓄力值并设置冷却时间，无论是否为玩家
        power -= 1
        skill1_cooldown = 2  # 2秒冷却
        print(f"Skill activated, new power: {power}")
        
        if skill_type == 1:  # 技能1
            print("Using skill 1")
            # 移动到对方位置并在对方蛐蛐身上播放剑气1.gif
            if is_player:
                if selected_side == "left":
                    # 调整移动距离，使其更大
                    target_x = start_x + 200  # 移动200像素
                    enemy_x = 450  # 右侧蛐蛐位置
                    enemy_y = 200  # 向上调整50像素
                    print(f"Player on left, moving to {target_x}, playing gif at {enemy_x}, {enemy_y}")
                else:
                    # 调整移动距离，使其更大
                    target_x = start_x - 200  # 移动200像素
                    enemy_x = 150  # 左侧蛐蛐位置
                    enemy_y = 200  # 向上调整50像素
                    print(f"Player on right, moving to {target_x}, playing gif at {enemy_x}, {enemy_y}")
            else:  # 敌人使用技能1
                if selected_side == "left":  # 玩家在左侧，敌人在右侧
                    target_x = start_x - 200  # 敌人从右侧向左移动
                    enemy_x = 150  # 左侧玩家蛐蛐位置
                    enemy_y = 200  # 向上调整50像素
                    print(f"Enemy on right, moving to {target_x}, playing gif at {enemy_x}, {enemy_y}")
                else:  # 玩家在右侧，敌人在左侧
                    target_x = start_x + 200  # 敌人从左侧向右移动
                    enemy_x = 450  # 右侧玩家蛐蛐位置
                    enemy_y = 200  # 向上调整50像素
                    print(f"Enemy on left, moving to {target_x}, playing gif at {enemy_x}, {enemy_y}")
            
            # 移动到对方位置
            def attack_callback():
                global enemy_health, player_health, enemy_health_label, player_health_label
                print("Attack callback called, playing gif")
                play_gif(canvas, "剑气1.gif", enemy_x, enemy_y, (100, 100), 2000)
                print("Starting 2 second delay before moving back")
                # 使用after方法代替time.sleep，避免阻塞主线程
                def move_back():
                    global enemy_health, player_health, enemy_health_label, player_health_label, current_turn, turn_label
                    print("Moving back")
                    # 扣除对方生命值
                    if is_player:
                        # 无论玩家在左侧还是右侧，玩家使用技能1都应该扣除敌人的生命值
                        enemy_health -= 2
                        if enemy_health < 0:
                            enemy_health = 0
                        enemy_health_label.config(text=f"对手: {enemy_health}")
                        print(f"Enemy health: {enemy_health}")
                    else:  # 敌人使用技能
                        # 无论玩家在左侧还是右侧，AI使用技能1都应该扣除玩家的生命值
                        player_health -= 2
                        if player_health < 0:
                            player_health = 0
                        player_health_label.config(text=f"玩家: {player_health}")
                        print(f"Player health: {player_health}")
                    move_cricket(canvas, cricket_id, target_x, start_y, start_x, start_y)
                    
                    # 切换回合
                    if is_player:
                        current_turn = "ai"
                        turn_label.config(text="当前回合: AI")
                        print("切换到AI回合")
                    else:
                        current_turn = "player"
                        turn_label.config(text="当前回合: 玩家")
                        print("切换到玩家回合")
                        # 重置AI决策标记
                        global ai_turn_in_progress
                        ai_turn_in_progress = False
                        print(f"技能使用完成，AI决策标记重置为: {ai_turn_in_progress}")
                canvas.after(2000, move_back)
            
            move_cricket(canvas, cricket_id, start_x, start_y, target_x, start_y, attack_callback)
        
        elif skill_type == 3:  # 技能3
            print("Using skill 3")
            # 蛐蛐不动，在两只蛐蛐中间播放剑气2.gif
            if is_player:
                if selected_side == "left":
                    # 左侧蛐蛐位置，右侧蛐蛐位置应该是450（600 * 3 // 4）
                    center_x = (start_x + 450) / 2  # 中间位置
                    center_y = 200  # 向上调整50像素
                    print(f"Player on left, playing gif at center: {center_x}, {center_y}")
                else:
                    # 右侧蛐蛐位置，左侧蛐蛐位置应该是150（600 // 4）
                    center_x = (start_x + 150) / 2  # 中间位置
                    center_y = 200  # 向上调整50像素
                    print(f"Player on right, playing gif at center: {center_x}, {center_y}")
            else:  # 敌人使用技能3
                if selected_side == "left":  # 玩家在左侧，敌人在右侧
                    # 右侧蛐蛐位置，左侧蛐蛐位置应该是150（600 // 4）
                    center_x = (start_x + 150) / 2  # 中间位置
                    center_y = 200  # 向上调整50像素
                    print(f"Enemy on right, playing gif at center: {center_x}, {center_y}")
                else:  # 玩家在右侧，敌人在左侧
                    # 左侧蛐蛐位置，右侧蛐蛐位置应该是450（600 * 3 // 4）
                    center_x = (start_x + 450) / 2  # 中间位置
                    center_y = 200  # 向上调整50像素
                    print(f"Enemy on left, playing gif at center: {center_x}, {center_y}")
            
            # 播放剑气特效，确保播放时间为1秒
            print("Playing剑气2.gif")
            play_gif(canvas, "剑气2.gif", center_x, center_y, (150, 100), 1000)
            
            # 1秒后扣除对方生命值
            def deduct_health():
                global enemy_health, player_health, enemy_health_label, player_health_label, current_turn, turn_label
                # 扣除对方生命值
                if is_player:
                    # 无论玩家在左侧还是右侧，玩家使用技能3都应该扣除敌人的生命值
                    enemy_health -= 2
                    if enemy_health < 0:
                        enemy_health = 0
                    enemy_health_label.config(text=f"对手: {enemy_health}")
                    print(f"Enemy health: {enemy_health}")
                else:  # 敌人使用技能
                    # 无论玩家在左侧还是右侧，AI使用技能3都应该扣除玩家的生命值
                    player_health -= 2
                    if player_health < 0:
                        player_health = 0
                    player_health_label.config(text=f"玩家: {player_health}")
                    print(f"Player health: {player_health}")
                
                # 切换回合
                if is_player:
                    current_turn = "ai"
                    turn_label.config(text="当前回合: AI")
                    print("切换到AI回合")
                else:
                    current_turn = "player"
                    turn_label.config(text="当前回合: 玩家")
                    print("切换到玩家回合")
                    # 重置AI决策标记
                    global ai_turn_in_progress
                    ai_turn_in_progress = False
                    print(f"技能使用完成，AI决策标记重置为: {ai_turn_in_progress}")
            
            canvas.after(1000, deduct_health)
    else:
        print("蓄力不足或技能冷却中")

# 技能2和4（加血技能）
def use_skill2(root, is_player=True):
    global power, player_health, enemy_health, skill2_cooldown, current_turn, turn_label, player_health_label, enemy_health_label
    
    # 检查回合
    if is_player and current_turn != "player":
        print("不是玩家回合，无法使用技能")
        return
    
    if not is_player and current_turn != "ai":
        print("不是AI回合，无法使用技能")
        return
    
    # 检查蓄力和冷却
    if power >= 2 and skill2_cooldown <= 0:
        power -= 2
        skill2_cooldown = 2  # 2秒冷却
        
        # 增加生命值
        if is_player:
            player_health += 3
            if player_health > 10:
                player_health = 10
            player_health_label.config(text=f"玩家: {player_health}")
        else:  # AI使用技能2
            enemy_health += 3
            if enemy_health > 10:
                enemy_health = 10
            enemy_health_label.config(text=f"对手: {enemy_health}")
        
        # 播放音效
        play_sound("我的刀盾.mp3")
        
        # 切换回合
        if is_player:
            current_turn = "ai"
            turn_label.config(text="当前回合: AI")
            print("切换到AI回合")
        else:
            current_turn = "player"
            turn_label.config(text="当前回合: 玩家")
            print("切换到玩家回合")
            # 重置AI决策标记
            global ai_turn_in_progress
            ai_turn_in_progress = False
            print(f"技能使用完成，AI决策标记重置为: {ai_turn_in_progress}")
    else:
        print("蓄力不足或技能冷却中")

# 大招
def use_ult(root, canvas, cricket_id, start_x, start_y, is_player=True):
    global power, ult_cooldown, player_health, enemy_health, current_turn, turn_label
    
    # 检查回合
    if is_player and current_turn != "player":
        print("不是玩家回合，无法使用技能")
        return
    
    if not is_player and current_turn != "ai":
        print("不是AI回合，无法使用技能")
        return
    
    # 检查蓄力和冷却
    if power >= 4 and ult_cooldown <= 0:
        power -= 4
        ult_cooldown = 5  # 5秒冷却
        
        # 播放音效
        play_sound("颗秒.mp3")
        
        # 移动攻击
        if is_player:
            if selected_side == "left":
                # 调整移动距离，使其更大
                target_x = start_x + 150  # 移动150像素
            else:
                # 调整移动距离，使其更大
                target_x = start_x - 150  # 移动150像素
        else:  # AI使用大招
            if selected_side == "left":  # 玩家在左侧，AI在右侧
                target_x = start_x - 150  # AI从右侧向左移动
            else:  # 玩家在右侧，AI在左侧
                target_x = start_x + 150  # AI从左侧向右移动
        
        # 移动攻击
        def attack_callback():
            global enemy_health, player_health, enemy_health_label, player_health_label, current_turn, turn_label
            # 扣除对方生命值
            if is_player:
                # 无论玩家在左侧还是右侧，玩家使用大招都应该扣除敌人的生命值
                enemy_health -= 4  # 大招伤害更高
                if enemy_health < 0:
                    enemy_health = 0
                enemy_health_label.config(text=f"对手: {enemy_health}")
                print(f"敌人生命值: {enemy_health}")
            else:  # 敌人使用技能
                # 无论玩家在左侧还是右侧，AI使用大招都应该扣除玩家的生命值
                player_health -= 4
                if player_health < 0:
                    player_health = 0
                player_health_label.config(text=f"玩家: {player_health}")
                print(f"玩家生命值: {player_health}")
            # 攻击后返回
            def move_back():
                global current_turn, turn_label
                move_cricket(canvas, cricket_id, target_x, start_y, start_x, start_y)
                # 切换回合
                if is_player:
                    current_turn = "ai"
                    turn_label.config(text="当前回合: AI")
                    print("切换到AI回合")
                else:
                    current_turn = "player"
                    turn_label.config(text="当前回合: 玩家")
                    print("切换到玩家回合")
                    # 重置AI决策标记
                    global ai_turn_in_progress
                    ai_turn_in_progress = False
                    print(f"技能使用完成，AI决策标记重置为: {ai_turn_in_progress}")
            canvas.after(1000, move_back)
        
        move_cricket(canvas, cricket_id, start_x, start_y, target_x, start_y, attack_callback)
    else:
        print("蓄力不足或技能冷却中")

# 游戏主界面
def game_window():
    global current_window, player_name, cricket_name, selected_side, power, power_label
    global player_health, enemy_health, player_health_label, enemy_health_label
    global cricket1_x, cricket1_y, cricket2_x, cricket2_y, window_x, window_y
    
    # 设置默认值，确保游戏能够正常运行
    if not selected_side:
        selected_side = "left"  # 默认选择左侧蛐蛐
    if not player_name:
        player_name = "玩家"  # 默认玩家名称
    if not cricket_name:
        cricket_name = "蛐蛐"  # 默认蛐蛐名称
    
    # 保存当前窗口位置（如果窗口存在）
    if current_window and current_window.winfo_exists():
        try:
            # 获取当前窗口位置
            window_geometry = current_window.winfo_geometry()
            # 提取位置信息
            if '+' in window_geometry:
                pos = window_geometry.split('+')
                if len(pos) >= 3:
                    window_x = int(pos[1])
                    window_y = int(pos[2])
        except Exception as e:
            print(f"获取窗口位置失败: {e}")
        try:
            # 关闭当前窗口
            current_window.destroy()
        except Exception as e:
            print(f"销毁窗口失败: {e}")
    
    # 根据难度设置游戏参数
    if difficulty == "简单":
        ai_health = 8  # 敌人生命值减少
        ai_power_gain = 1  # 敌人蓄力获取速度正常
        ai_damage = 1.5  # 敌人伤害降低
    elif difficulty == "普通":
        ai_health = 10  # 敌人生命值正常
        ai_power_gain = 1  # 敌人蓄力获取速度正常
        ai_damage = 1  # 敌人伤害正常
    else:  # 困难
        ai_health = 12  # 敌人生命值增加
        ai_power_gain = 1.5  # 敌人蓄力获取速度加快
        ai_damage = 1.5  # 敌人伤害增加
    
    # 重置游戏状态
    power = 0
    player_health = 10
    enemy_health = ai_health
    print(f"游戏开始，蓄力值重置为0，玩家生命值重置为10，敌人生命值重置为{ai_health}")  # 调试信息
    
    # 创建游戏窗口
    root = tk.Tk()
    root.title("小游戏：电子斗蛐蛐")
    current_window = root
    
    # 固定窗口大小为600x400，与菜单一致
    window_width, window_height = 600, 400
    
    # 加载背景图片
    background_image, _, _ = load_background("舞台1.jpg", (window_width, window_height))
    
    # 设置窗口大小并锁定
    root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
    root.resizable(False, False)
    
    # 加载蛐蛐图片
    cricket1_image = load_image("1.jpg")
    cricket2_image = load_image("2.jpg")
    
    # 加载技能图片
    left_skills, right_skills = load_skill_images()
    
    # 创建画布
    canvas = tk.Canvas(root, width=window_width, height=window_height)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # 显示背景图片（居中）
    if background_image:
        canvas.create_image(window_width//2, window_height//2, image=background_image, anchor=tk.CENTER)
    else:
        canvas.create_rectangle(0, 0, window_width, window_height, fill="lightgreen")
    
    # 绘制标题
    canvas.create_text(window_width//2, 50, text="电子斗蛐蛐", font=('Arial', 24, 'bold'), fill="brown")
    
    # 显示玩家信息
    if player_name:
        canvas.create_text(100, 30, text=f"玩家: {player_name}", font=('Arial', 12), fill="brown")
    
    # 显示生命值
    # 根据玩家选择的蛐蛐位置调整血量标签的位置
    if selected_side == "left":
        # 玩家在左侧，敌人在右侧
        player_health_label = tk.Label(root, text=f"玩家: {player_health}", font=('Arial', 14, 'bold'), bg="white", bd=2, relief="solid")
        player_health_label.place(x=20, y=20, width=100, height=30)
        
        enemy_health_label = tk.Label(root, text=f"对手: {enemy_health}", font=('Arial', 14, 'bold'), bg="white", bd=2, relief="solid")
        enemy_health_label.place(x=480, y=20, width=100, height=30)
    else:
        # 玩家在右侧，敌人在左侧
        player_health_label = tk.Label(root, text=f"玩家: {player_health}", font=('Arial', 14, 'bold'), bg="white", bd=2, relief="solid")
        player_health_label.place(x=480, y=20, width=100, height=30)
        
        enemy_health_label = tk.Label(root, text=f"对手: {enemy_health}", font=('Arial', 14, 'bold'), bg="white", bd=2, relief="solid")
        enemy_health_label.place(x=20, y=20, width=100, height=30)
    
    # 显示当前回合
    global current_turn, turn_label
    current_turn = "player"  # 游戏开始时玩家先行动
    turn_label = tk.Label(root, text=f"当前回合: 玩家", font=('Arial', 14, 'bold'), bg="white", bd=2, relief="solid")
    turn_label.place(x=250, y=20, width=120, height=30)
    
    # 玩家回合时间限制，10秒后自动切换到AI回合
    def check_player_turn():
        global current_turn, turn_label
        if current_turn == "player":
            print("玩家回合超时，切换到AI回合")
            current_turn = "ai"
            turn_label.config(text="当前回合: AI")
    
    # 10秒后检查玩家回合是否超时
    root.after(10000, check_player_turn)
    
    # 显示蛐蛐图片
    cricket_x1 = window_width // 4
    cricket_x2 = window_width * 3 // 4
    cricket_y = window_height // 2
    
    # 保存蛐蛐ID
    cricket1_id = None
    cricket2_id = None
    
    # 显示左侧蛐蛐
    if cricket1_image:
        cricket1_id = canvas.create_image(cricket_x1, cricket_y, image=cricket1_image)
    else:
        cricket1_id = canvas.create_text(cricket_x1, cricket_y, text="蛐蛐1", font=('Arial', 16), fill="red")
    
    # 显示右侧蛐蛐
    if cricket2_image:
        cricket2_id = canvas.create_image(cricket_x2, cricket_y, image=cricket2_image)
    else:
        cricket2_id = canvas.create_text(cricket_x2, cricket_y, text="蛐蛐2", font=('Arial', 16), fill="blue")
    
    # 显示蛐蛐名称（上方）
    if selected_side == "left" and cricket_name:
        canvas.create_text(cricket_x1, cricket_y - 100, text=cricket_name, font=('Arial', 14, 'bold'), fill="red")
        canvas.create_text(cricket_x2, cricket_y - 100, text="对手蛐蛐", font=('Arial', 14), fill="blue")
    elif selected_side == "right" and cricket_name:
        canvas.create_text(cricket_x1, cricket_y - 100, text="对手蛐蛐", font=('Arial', 14), fill="red")
        canvas.create_text(cricket_x2, cricket_y - 100, text=cricket_name, font=('Arial', 14, 'bold'), fill="blue")
    else:
        canvas.create_text(cricket_x1, cricket_y - 100, text="蛐蛐1", font=('Arial', 14), fill="red")
        canvas.create_text(cricket_x2, cricket_y - 100, text="蛐蛐2", font=('Arial', 14), fill="blue")
    
    # 显示左侧蛐蛐技能（左下角）
    skill_x = cricket_x1 - 60
    skill_y = cricket_y + 100
    left_skill_buttons = []
    for i, skill in enumerate(left_skills):
        if skill:
            # 只有玩家选择左侧蛐蛐时，左侧技能才可用
            if selected_side == "left":
                button = tk.Button(root, image=skill, command=lambda i=i:
                    (use_skill1(root, canvas, cricket1_id, cricket_x1, cricket_y) if i == 0 else
                     use_skill2(root) if i == 1 else
                     use_ult(root, canvas, cricket1_id, cricket_x1, cricket_y))
                , borderwidth=0, highlightthickness=0, relief=tk.FLAT)
            else:
                # 禁用对方技能
                button = tk.Button(root, image=skill, state=tk.DISABLED, borderwidth=0, highlightthickness=0, relief=tk.FLAT)
            button.place(x=skill_x + i * 60, y=skill_y, width=50, height=50)
            left_skill_buttons.append(button)
    
    # 显示右侧蛐蛐技能（右下角）
    skill_x = cricket_x2 - 60
    skill_y = cricket_y + 100
    right_skill_buttons = []
    for i, skill in enumerate(right_skills):
        if skill:
            # 只有玩家选择右侧蛐蛐时，右侧技能才可用
            if selected_side == "right":
                button = tk.Button(root, image=skill, command=lambda i=i:
                    (use_skill1(root, canvas, cricket2_id, cricket_x2, cricket_y, skill_type=3) if i == 0 else
                     use_skill2(root) if i == 1 else
                     use_ult(root, canvas, cricket2_id, cricket_x2, cricket_y))
                , borderwidth=0, highlightthickness=0, relief=tk.FLAT)
            else:
                # 禁用对方技能
                button = tk.Button(root, image=skill, state=tk.DISABLED, borderwidth=0, highlightthickness=0, relief=tk.FLAT)
            button.place(x=skill_x + i * 60, y=skill_y, width=50, height=50)
            right_skill_buttons.append(button)
    
    # 创建蓄力条标签（左下角，数字显示）
    power_label = tk.Label(root, text=f"{power}/{power_max}", font=('Arial', 14, 'bold'), bg="white", bd=2, relief="solid")
    power_label.place(x=20, y=window_height - 60, width=100, height=30)
    
    # 开始蓄力条更新
    root.after(1000, lambda: update_power(root))  # 1秒后开始更新
    print("蓄力条更新已启动")  # 调试信息
    
    # 定期检查血量
    def check_health():
        global enemy_health, player_health
        if enemy_health <= 0:
            # 显示胜利动画
            show_win_animation(root, canvas, True)
        elif player_health <= 0:
            # 显示失败动画
            show_win_animation(root, canvas, False)
        else:
            # 继续检查
            root.after(500, check_health)
    
    # 开始检查
    root.after(500, check_health)
    print("敌人血量检查已启动")  # 调试信息
    
    # AI决策循环
    ai_turn_in_progress = False  # 标记AI决策是否正在进行中
    
    def ai_turn():
        global enemy_health, player_health, power, current_turn, turn_label, skill1_cooldown, skill2_cooldown, ult_cooldown
        nonlocal ai_turn_in_progress
        
        # 打印调试信息
        print(f"AI回合检查: current_turn={current_turn}, ai_turn_in_progress={ai_turn_in_progress}, enemy_health={enemy_health}, player_health={player_health}")
        print(f"AI状态: power={power}, skill1_cooldown={skill1_cooldown}, skill2_cooldown={skill2_cooldown}, ult_cooldown={ult_cooldown}")
        
        # 当回合切换到玩家时，重置AI决策标记
        if current_turn == "player":
            ai_turn_in_progress = False
            print(f"回合切换到玩家，AI决策标记重置为: {ai_turn_in_progress}")
        
        # 只有游戏进行中且是AI回合且决策未在进行中时才执行AI决策
        if enemy_health > 0 and player_health > 0 and current_turn == "ai" and not ai_turn_in_progress:
            print("AI开始决策")
            # 标记AI决策开始
            ai_turn_in_progress = True
            print(f"AI决策开始，标记设置为: {ai_turn_in_progress}")
            
            # 确定AI控制的蛐蛐
            ai_cricket_id = cricket2_id if selected_side == "left" else cricket1_id
            ai_x = cricket_x2 if selected_side == "left" else cricket_x1
            ai_y = cricket_y
            
            # 确定AI的蓄力值和生命值
            ai_power = power  # 暂时使用相同的蓄力值
            ai_health = enemy_health if selected_side == "left" else player_health
            player_current_health = player_health if selected_side == "left" else enemy_health
            
            # 检查是否有可用技能
            def has_available_skill():
                # 检查技能1或3是否可用
                if power >= 1 and skill1_cooldown <= 0:
                    return True
                # 检查技能2是否可用
                if power >= 2 and skill2_cooldown <= 0:
                    return True
                # 检查技能4是否可用
                if power >= 3 and ult_cooldown <= 0:
                    return True
                return False
            
            if has_available_skill():
                print("AI有可用技能，调用AI决策函数")
                # 调用AI决策函数
                ai_make_decision(root, canvas, ai_cricket_id, ai_x, ai_y, ai_power, ai_health, player_current_health)
            else:
                # 没有可用技能，直接切换到玩家回合
                print("AI没有可用技能，切换到玩家回合")
                current_turn = "player"
                turn_label.config(text="当前回合: 玩家")
                # 标记AI决策结束
                ai_turn_in_progress = False
                print(f"AI决策结束，标记重置为: {ai_turn_in_progress}")
        
        # 设置AI决策间隔为300毫秒，确保AI在3秒内做出决策
        delay = 300  # 300毫秒
        
        # 安排下一次AI决策
        print(f"安排下一次AI决策，延迟: {delay}ms")
        root.after(delay, ai_turn)
    
    # 开始AI决策循环
    root.after(2000, ai_turn)  # 2秒后开始AI决策
    print("AI决策循环已启动")  # 调试信息
    
    # 保持图片引用
    root.bg_img = background_image
    root.c1_img = cricket1_image
    root.c2_img = cricket2_image
    root.left_skills = left_skills
    root.right_skills = right_skills
    root.left_skill_buttons = left_skill_buttons
    root.right_skill_buttons = right_skill_buttons
    
    # 运行主循环
    root.mainloop()



# 选择蛐蛐侧边
def select_side(side):
    global selected_side
    selected_side = side
    game_window()

# 输入蛐蛐名称界面
def input_cricket_name():
    global current_window, cricket_name, window_x, window_y
    
    # 保存当前窗口位置（如果窗口存在）
    if current_window and current_window.winfo_exists():
        try:
            # 获取当前窗口位置
            window_geometry = current_window.winfo_geometry()
            # 提取位置信息
            if '+' in window_geometry:
                pos = window_geometry.split('+')
                if len(pos) >= 3:
                    window_x = int(pos[1])
                    window_y = int(pos[2])
        except Exception as e:
            print(f"获取窗口位置失败: {e}")
        try:
            # 关闭当前窗口
            current_window.destroy()
        except Exception as e:
            print(f"销毁窗口失败: {e}")
    
    # 创建输入窗口
    root = tk.Tk()
    root.title("小游戏：电子斗蛐蛐")
    root.geometry(f"600x400+{window_x}+{window_y}")
    root.resizable(False, False)
    current_window = root
    
    # 设置背景
    root.configure(bg="lightgreen")
    
    # 创建标题
    title_label = tk.Label(root, text="给你的蛐蛐起个名字", font=('Arial', 24, 'bold'), bg="lightgreen", fg="brown")
    title_label.pack(pady=40)
    
    # 创建输入框架
    input_frame = tk.Frame(root, bg="lightgreen")
    input_frame.pack(pady=20)
    
    # 输入标签
    name_label = tk.Label(input_frame, text="蛐蛐名称:", font=('Arial', 16), bg="lightgreen")
    name_label.grid(row=0, column=0, padx=10, pady=10)
    
    # 输入框
    name_entry = tk.Entry(input_frame, font=('Arial', 16), width=20)
    name_entry.grid(row=0, column=1, padx=10, pady=10)
    
    # 确认按钮
    def confirm_name():
        global cricket_name
        cricket_name = name_entry.get().strip()
        if cricket_name:
            select_side("left")
        else:
            # 显示错误提示
            error_label = tk.Label(input_frame, text="请输入蛐蛐名称", font=('Arial', 12), bg="lightgreen", fg="red")
            error_label.grid(row=1, column=0, columnspan=2, pady=10)
    
    confirm_button = tk.Button(
        input_frame, 
        text="确认", 
        font=('Arial', 14), 
        width=10, 
        command=confirm_name
    )
    confirm_button.grid(row=2, column=0, columnspan=2, pady=20)
    
    # 返回按钮（左下角）
    def back_to_menu():
        global current_window
        # 先将current_window设置为None，避免在start_menu中尝试销毁已销毁的窗口
        current_window = None
        root.destroy()
        start_menu()
    
    back_button = tk.Button(
        root, 
        text="返回", 
        font=('Arial', 12), 
        width=8, 
        command=back_to_menu
    )
    back_button.place(x=20, y=350)
    
    # 运行主循环
    root.mainloop()

# 输入用户名界面
def input_username():
    global current_window, player_name, window_x, window_y
    
    # 保存当前窗口位置（如果窗口存在）
    if current_window and current_window.winfo_exists():
        try:
            # 获取当前窗口位置
            window_geometry = current_window.winfo_geometry()
            # 提取位置信息
            if '+' in window_geometry:
                pos = window_geometry.split('+')
                if len(pos) >= 3:
                    window_x = int(pos[1])
                    window_y = int(pos[2])
        except Exception as e:
            print(f"获取窗口位置失败: {e}")
        try:
            # 关闭当前窗口
            current_window.destroy()
        except Exception as e:
            print(f"销毁窗口失败: {e}")
    
    # 创建输入窗口
    root = tk.Tk()
    root.title("小游戏：电子斗蛐蛐")
    root.geometry(f"600x400+{window_x}+{window_y}")
    root.resizable(False, False)
    current_window = root
    
    # 设置背景
    root.configure(bg="lightgreen")
    
    # 创建标题
    title_label = tk.Label(root, text="欢迎来到电子斗蛐蛐", font=('Arial', 24, 'bold'), bg="lightgreen", fg="brown")
    title_label.pack(pady=40)
    
    # 创建输入框架
    input_frame = tk.Frame(root, bg="lightgreen")
    input_frame.pack(pady=20)
    
    # 输入标签
    name_label = tk.Label(input_frame, text="用户名:", font=('Arial', 16), bg="lightgreen")
    name_label.grid(row=0, column=0, padx=10, pady=10)
    
    # 输入框
    name_entry = tk.Entry(input_frame, font=('Arial', 16), width=20)
    name_entry.grid(row=0, column=1, padx=10, pady=10)
    
    # 确认按钮
    def confirm_username():
        global player_name
        player_name = name_entry.get().strip()
        if player_name:
            # 保存玩家数据
            save_player_data(player_name)
            # 显示登录成功信息
            success_label = tk.Label(input_frame, text="登录成功！", font=('Arial', 12), bg="lightgreen", fg="green")
            success_label.grid(row=1, column=0, columnspan=2, pady=10)
            # 2秒后返回主菜单
            root.after(2000, lambda: (root.destroy(), start_menu()))
        else:
            # 显示错误提示
            error_label = tk.Label(input_frame, text="请输入用户名", font=('Arial', 12), bg="lightgreen", fg="red")
            error_label.grid(row=1, column=0, columnspan=2, pady=10)
    
    confirm_button = tk.Button(
        input_frame, 
        text="确认", 
        font=('Arial', 14), 
        width=10, 
        command=confirm_username
    )
    confirm_button.grid(row=2, column=0, columnspan=2, pady=20)
    
    # 返回按钮（左下角）
    def back_to_menu():
        global current_window
        # 先将current_window设置为None，避免在start_menu中尝试销毁已销毁的窗口
        current_window = None
        root.destroy()
        start_menu()
    
    back_button = tk.Button(
        root, 
        text="返回", 
        font=('Arial', 12), 
        width=8, 
        command=back_to_menu
    )
    back_button.place(x=20, y=350)
    
    # 运行主循环
    root.mainloop()

# 登出功能
def logout():
    """登出当前账号"""
    clear_player_data()
    global player_name, cricket_name, selected_side
    player_name = ""
    cricket_name = ""
    selected_side = ""
    start_menu()

# 开始菜单
def start_menu():
    global current_window, player_name, window_x, window_y
    
    # 保存当前窗口位置（如果窗口存在）
    if current_window and current_window.winfo_exists():
        try:
            # 获取当前窗口位置
            window_geometry = current_window.winfo_geometry()
            # 提取位置信息
            if '+' in window_geometry:
                pos = window_geometry.split('+')
                if len(pos) >= 3:
                    window_x = int(pos[1])
                    window_y = int(pos[2])
        except Exception as e:
            print(f"获取窗口位置失败: {e}")
        try:
            # 关闭当前窗口
            current_window.destroy()
        except Exception as e:
            print(f"销毁窗口失败: {e}")
    
    # 创建菜单窗口
    root = tk.Tk()
    root.title("小游戏：电子斗蛐蛐")
    root.geometry(f"600x400+{window_x}+{window_y}")
    root.resizable(False, False)
    current_window = root
    
    # 设置背景
    root.configure(bg="lightgreen")
    
    # 创建标题
    title_label = tk.Label(root, text="电子斗蛐蛐", font=('Arial', 32, 'bold'), bg="lightgreen", fg="brown")
    title_label.pack(pady=60)
    
    # 创建按钮框架
    button_frame = tk.Frame(root, bg="lightgreen")
    button_frame.pack(pady=20)
    
    # 开始游戏按钮
    def start_game():
        if player_name:
            input_cricket_name()
        else:
            # 未登录，跳转到登录界面
            input_username()
    
    start_button = tk.Button(
        button_frame, 
        text="开始游戏", 
        font=('Arial', 18), 
        width=15, 
        height=2, 
        command=start_game
    )
    start_button.pack(pady=10)
    
    # 登录游戏按钮
    login_button = tk.Button(
        button_frame, 
        text="登录游戏", 
        font=('Arial', 18), 
        width=15, 
        height=2, 
        command=input_username
    )
    login_button.pack(pady=10)
    
    # 难度选择按钮
    def open_difficulty_selection():
        # 创建难度选择窗口
        difficulty_window = tk.Toplevel(root)
        difficulty_window.title("选择难度")
        difficulty_window.geometry(f"400x300+{window_x+100}+{window_y+50}")
        difficulty_window.resizable(False, False)
        difficulty_window.configure(bg="lightgreen")
        
        # 难度选择标题
        difficulty_title = tk.Label(difficulty_window, text="选择难度", font=('Arial', 20, 'bold'), bg="lightgreen", fg="brown")
        difficulty_title.pack(pady=30)
        
        # 难度按钮框架
        difficulty_buttons = tk.Frame(difficulty_window, bg="lightgreen")
        difficulty_buttons.pack(pady=20)
        
        # 难度选择函数
        def set_difficulty(level):
            global difficulty
            difficulty = level
            # 显示选择结果
            result_label.config(text=f"已选择: {difficulty}")
        
        # 简单难度按钮
        easy_button = tk.Button(
            difficulty_buttons, 
            text="简单", 
            font=('Arial', 14), 
            width=8, 
            command=lambda: set_difficulty("简单")
        )
        easy_button.pack(side=tk.LEFT, padx=10)
        
        # 普通难度按钮
        normal_button = tk.Button(
            difficulty_buttons, 
            text="普通", 
            font=('Arial', 14), 
            width=8, 
            command=lambda: set_difficulty("普通")
        )
        normal_button.pack(side=tk.LEFT, padx=10)
        
        # 困难难度按钮
        hard_button = tk.Button(
            difficulty_buttons, 
            text="困难", 
            font=('Arial', 14), 
            width=8, 
            command=lambda: set_difficulty("困难")
        )
        hard_button.pack(side=tk.LEFT, padx=10)
        
        # 显示当前选择
        result_label = tk.Label(difficulty_window, text=f"当前难度: {difficulty}", font=('Arial', 14), bg="lightgreen", fg="blue")
        result_label.pack(pady=20)
        
        # 确定按钮
        confirm_button = tk.Button(
            difficulty_window, 
            text="确定", 
            font=('Arial', 14), 
            width=10, 
            command=difficulty_window.destroy
        )
        confirm_button.pack(pady=20)
    
    difficulty_button = tk.Button(
        button_frame, 
        text="难度选择", 
        font=('Arial', 18), 
        width=15, 
        height=2, 
        command=open_difficulty_selection
    )
    difficulty_button.pack(pady=10)
    
    # 退出游戏按钮
    exit_button = tk.Button(
        button_frame, 
        text="退出游戏", 
        font=('Arial', 18), 
        width=15, 
        height=2, 
        command=root.quit
    )
    exit_button.pack(pady=10)
    
    # 显示当前登录用户
    if player_name:
        user_label = tk.Label(root, text=f"当前登录: {player_name}", font=('Arial', 14), bg="lightgreen", fg="blue")
        user_label.pack(pady=20)
    
    # 运行主循环
    root.mainloop()

# 运行开始菜单
if __name__ == "__main__":
    # 尝试加载已保存的玩家数据
    saved_player = load_player_data()
    if saved_player:
        player_name = saved_player
        print(f"自动登录: {player_name}")
    print(f"游戏启动 - 声音可用状态: {sound_available}")
    start_menu()
