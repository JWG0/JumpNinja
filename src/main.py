import random
import pygame
import xlrd
from xlutils.copy import copy
from sys import exit
#初始化
pygame.init()
# 屏幕大小的常量
SCREEN_RECT = pygame.Rect(0, 0, 480, 700)#Rect(x, y, width, height)
# 刷新的帧率
FRAME_PER_SEC = 60
# 创建障碍物的定时器常量
CREATE_OBSTACLE_EVENT = pygame.USEREVENT
# 创建技能点事件
CREATE_SHILL_EVENT = pygame.USEREVENT+1
#金币事件
CREATE_GOLD_EVENT=pygame.USEREVENT+2

#播放背景音乐
pygame.mixer.init()
pygame.mixer.music.load ('audios/game_music.WAV')
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume (0.25)
class GameSprite(pygame.sprite.Sprite):
    """精灵"""
    wall_thick=43#两边墙壁厚度
    def __init__(self, image_object, speed_x=0,speed_y=0):
        # 调用父类的初始化方法
        super().__init__()
        # 定义对象的属性
        self.image = image_object
        self.rect = self.image.get_rect()#self.rect=self.image.get_rect()获得image距形大小
        self.speed_x = speed_x      #创建类属性speed
        self.speed_y=speed_y    #创建类属性speed_hero_y，表示hero上下移动的速度
    def update(self):
        # 在屏幕的垂直方向上移动
        self.rect.y += self.speed_y   #更新敌机的坐标,更新子弹坐标,更新背景图片坐标
        self.rect.x+=self.speed_x

class class_background(GameSprite):
    """游戏背景精灵"""
    def __init__(self,image, speed_x,speed_y=2,is_bg2=False):
        image_object=pygame.image.load(image)
        # 1. 调用父类方法实现精灵的创建(image/rect/speed)
        super().__init__(image_object,speed_x,speed_y)
        # 2. 判断是否是交替图像，如果是，需要设置初始位置
        if is_bg2:#bg2初始化为（0，-800）
            self.rect.y = -self.rect.height#800

    def update(self):
        # 1. 调用父类的方法实现
        super().update()
        # 2. 判断是否移出屏幕，如果移出屏幕，将图像设置到屏幕的上方
        if self.rect.y >= SCREEN_RECT.height:
            self.rect.y = -self.rect.height#背景精灵画图的坐标,-700
class class_obstacle(GameSprite):
    """障碍物精灵"""
    speed_obstacle_max=6
    def __init__(self,image_object,rect_x=-1,rect_y=0):
        # 2. 指定障碍物的初始随机速度
        self.speed = random.randint(2,class_obstacle.speed_obstacle_max)
        # 1. 调用父类方法，创建敌机精灵，同时指定敌机图片
        super().__init__(image_object,0,self.speed)
        # 3. 指定障碍物的初始随机位置
        self.rect.bottom = rect_y
        if rect_x!=-1:
            self.rect.x=rect_x
        else:
            max_x = SCREEN_RECT.width - self.rect.width - GameSprite.wall_thick
            min_x = GameSprite.wall_thick
            self.rect.x = random.randint(min_x, max_x)
    def update(self):
        # 1. 调用父类方法
        super().update()
        # 2. 判断是否飞出屏幕，如果是，需要从精灵组删除敌机
        if self.rect.y >= SCREEN_RECT.height:
            # print("飞出屏幕，需要从精灵组删除...")
            # kill方法可以将精灵从所有精灵组中移出，精灵就会被自动销毁
            self.kill()

    def __del__(self):
        MainGame.ninja.ninja_score+=1
        pass

class class_skill(GameSprite):
    """技能精灵"""
    skill_speed_max=4
    def __init__(self):
        # 2. 指定技能的初始随机速度
        self.speed = random.randint(2,class_skill.skill_speed_max)#max(random.randint(2,8),random.randint(2,10))
        #创建技能。1血包，2无敌，3吸铁石，4飞翔
        self.skill_kind=random.randint(1,3)
        # 1. 调用父类方法，创建敌机精灵，同时指定敌机图片
        super().__init__(MainGame.image_skill[self.skill_kind],0,self.speed)

        # 3. 指定障碍物的初始随机位置
        self.rect.bottom = 0
        max_x = SCREEN_RECT.width - self.rect.width-GameSprite.wall_thick
        min_x = GameSprite.wall_thick
        self.rect.x = random.randint(min_x, max_x)

    def update(self):
        # 1. 调用父类方法
        super().update()
        # 2. 判断是否飞出屏幕，如果是，需要从精灵组删除敌机
        if self.rect.y >= SCREEN_RECT.height:
            self.kill()
class class_finish(GameSprite):
    """终点线精灵"""
    def __init__(self):
        # 1. 调用父类方法
        super().__init__(MainGame.image_finish,0,2)
        self.rect.bottom = 0
        self.rect.x = 0

    def update(self):
        super().update()
        if self.rect.y >= SCREEN_RECT.height:
            self.kill()
class class_glod(GameSprite):
    """金币精灵"""
    def __init__(self,image_object,rect_x=0,rect_bottom=0,speed=2):#初始x坐标
        # 1. 调用父类方法，创建敌机精灵，同时指定敌机图片
        super().__init__(image_object,0,speed)
        # 3. 指定障碍物的初始随机位置
        self.rect.bottom = rect_bottom
        self.rect.x =rect_x

    def update(self):
        # 1. 调用父类方法
        super().update()
        if MainGame.skills_list[3]==1 and MainGame.skill_time[3]<=MainGame.skill_TIME :
            if abs(MainGame.ninja.rect.x-self.rect.x)<=300 and abs(MainGame.ninja.rect.y-self.rect.y)<=300:
                self.speed_x=(MainGame.ninja.rect.x-self.rect.x)/10
                self.speed_y = (MainGame.ninja.rect.y - self.rect.y)/10
            else:
                self.speed_x = 0
                self.speed_y = 2
        else:
            self.speed_x=0
            self.speed_y=2
        # 2. 判断是否飞出屏幕，如果是，需要从精灵组删除
        if self.rect.y >= SCREEN_RECT.height:
            self.kill()

    def __del__(self):
        pass

class class_ninja(GameSprite):
    """忍者精灵"""
    ninja_score=0#冲到的高度
    ninja_blood=5
    ninja_state=0#忍者所处的位置，应该用什么图片
    def __init__(self):

        # 1. 调用父类方法，设置image&speed
        super().__init__(pygame.image.load("images/ninja3_3.png"), 0)

        # 2. 设置忍者的初始位置
        self.temp=random.randint(0,1)#0是左边，1是右边
        self.rect.x =self.temp * SCREEN_RECT.width#左边或者右边
        if self.rect.x==0:
            self.rect.x+=GameSprite.wall_thick
        else:
            self.rect.x-=GameSprite.wall_thick
        self.rect.bottom = SCREEN_RECT.bottom-100
        ninja_state=self.temp*5
    def update(self):
        # 移动
        self.rect.x+=self.speed_x
        self.rect.y +=self.speed_y
        # 控制英雄不能离开屏幕,约束
        if self.rect.x < GameSprite.wall_thick:
            self.rect.x = GameSprite.wall_thick
        elif self.rect.right > SCREEN_RECT.right-GameSprite.wall_thick:
            self.rect.right = SCREEN_RECT.right-GameSprite.wall_thick
        if self.rect.x==GameSprite.wall_thick:#左边
            class_ninja.ninja_state=class_ninja.ninja_state+0.5
            if (class_ninja.ninja_state)%3==0:
                class_ninja.ninja_state = int(class_ninja.ninja_state) % 12#从0开始
                self.image=MainGame.images3_ninja[int(class_ninja.ninja_state/3)]
        elif self.rect.right == SCREEN_RECT.right-GameSprite.wall_thick:
            class_ninja.ninja_state = class_ninja.ninja_state + 0.5
            if (class_ninja.ninja_state) % 3 == 0:
                class_ninja.ninja_state = int(class_ninja.ninja_state) % 12
                self.image = MainGame.images9_ninja[int(class_ninja.ninja_state/3)]
        else:
            class_ninja.ninja_state = int(class_ninja.ninja_state) % 7 + 1
            self.image = MainGame.images6_ninja[class_ninja.ninja_state]
    def display_inija(self):
        pass
class MainGame():
    skill_time=[0,0,0,0,0,0]#技能维持时间
    skill_TIME=400
    skills_list = [0, 0, 0, 0, 0, 0, 0,0]
    Pause_button = pygame.image.load("images/pause_pressed.png")
    images3_ninja=[pygame.image.load("images/ninja3_3.png"),
                    pygame.image.load("images/ninja3_6.png"),
                    pygame.image.load("images/ninja3_9.png"),
                    pygame.image.load("images/ninja3_12.png")]
    images6_ninja=[0,pygame.image.load("images/ninja11.png"),
                    pygame.image.load("images/ninja12.png"),
                    pygame.image.load("images/ninja13.png"),
                    pygame.image.load("images/ninja14.png"),
                    pygame.image.load("images/ninja15.png"),
                    pygame.image.load("images/ninja16.png"),
                    pygame.image.load("images/ninja17.png")]#中间的翻转
    images9_ninja=[pygame.image.load("images/ninja9_3.png"),
                    pygame.image.load("images/ninja9_6.png"),
                    pygame.image.load("images/ninja9_9.png"),
                    pygame.image.load("images/ninja9_12.png")]
    image_skill=[0,
                 pygame.image.load("images/skill1.png"),
                 pygame.image.load("images/skill2.png"),
                 pygame.image.load("images/skill3.png"),]
    image_obstacle=pygame.image.load("images/obstalce1.png")
    image_glod=pygame.image.load("images/glod.png")
    Resume_button = pygame.image.load("images/resume.png")
    game_level=1#现在处于第一关
    game_score=[0,0,100,300,600,1200,2000,3000,4000,5000,6000,1000000000]#关卡所需要的分数
    image_finish=pygame.image.load("images/finish.png")
    # 1 加载游戏窗口
    screen = 0  # 这句话可以不要
    def __init__(self):
        # 1 调用显示模块的初始化
        pygame.display.init()  # 用pygame.init()也可以
        pygame.display.set_caption('跳跃忍者')  # 设置窗口标题
        # 1 创建窗口#静态变量
        MainGame.screen = pygame.display.set_mode([SCREEN_RECT.width,SCREEN_RECT.height])
        # 2. 创建游戏的时钟
        self.clock = pygame.time.Clock()
        # 3. 调用私有方法，精灵和精灵组的创建
        self.__create_sprites()
        # 4. 设置定时器事件 - 创建障碍物　1s
        pygame.time.set_timer(CREATE_OBSTACLE_EVENT, 2000)
        pygame.time.set_timer(CREATE_SHILL_EVENT,5000)
        pygame.time.set_timer(CREATE_GOLD_EVENT,3000)
    ninja = class_ninja()
    def __create_sprites(self):

        # 创建背景精灵
        bg0=class_background("images/bg0.jpg",0,0)
        bg1 = class_background("images/bg1.png",0,2)
        bg2 = class_background("images/bg2.png",0,2,True)
        # 创建背景精灵组
        self.group_background = pygame.sprite.Group(bg0,bg1, bg2)

        # 创建障碍物的精灵组
        self.group_obstalce= pygame.sprite.Group()

        # 创建技能的精灵组
        self.group_skill = pygame.sprite.Group()

        #创建金币精灵组
        self.group_glod=pygame.sprite.Group()

        #创建终点线精灵组
        self.group_finish=pygame.sprite.Group()

        # 创建英雄的精灵和精灵组
        self.group_ninja = pygame.sprite.Group(MainGame.ninja)
    def start_game(self):
        print("游戏开始...")
        while True:
            # 1. 设置刷新帧率
            self.clock.tick(FRAME_PER_SEC)
            # 2. 事件监听
            self.__event_handler()
            # 3. 碰撞检测
            self.__check_collide()
            # 4. 更新/绘制精灵组
            self.__update_sprites()
            # 5. 更新显示
            pygame.display.update()
            #其他
            MainGame.skill_time[1]+=1
            MainGame.skill_time[2] += 1
            MainGame.skill_time[3] += 1
    def __event_handler(self):
        for event in pygame.event.get():
            mouse_location=pygame.mouse.get_pos()
            L,M,R=pygame.mouse.get_pressed()
            pause=False
            if mouse_location[0]>420 and mouse_location[1]<45 and L:
                pause=True
            while pause:
                # 开始键
                MainGame.screen.blit(MainGame.Resume_button, (420, 0))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        MainGame.__game_over()
                    mouse_location = pygame.mouse.get_pos()
                    L, M, R = pygame.mouse.get_pressed()
                    if mouse_location[0] > 420 and mouse_location[1] < 45 and L:
                        pause = False
                        # 暂停键
                        MainGame.screen.blit(MainGame.Pause_button, (420, 0))
                pygame.display.update()
                self.clock.tick(15)#刷新帧率
            if event.type == pygame.QUIT:
                MainGame.__game_over()
            elif event.type == CREATE_OBSTACLE_EVENT:
                i = min(random.randint(1, MainGame.game_level),random.randint(1, MainGame.game_level))
                for i in range(0,i):#关卡越高，i的值可能越大
                    object_obstacle=class_obstacle(MainGame.image_obstacle)
                    # 将障碍物精灵添加到敌机精灵组
                    self.group_obstalce.add(object_obstacle)
            elif event.type == CREATE_SHILL_EVENT:#在产生技能时，同时产生几个障碍物
                i=random.randint(1,MainGame.game_level) #game_level越高，i==1概率越低
                if i==1 or i==2 or i==6:#当i等于1才可以产生
                    object_skill=class_skill()
                    self.group_skill.add(object_skill)
                    if MainGame.game_level > 1:
                        object_obstacle = class_obstacle(MainGame.image_obstacle, object_skill.rect.x, -40)  # 障碍物
                        self.group_obstalce.add(object_obstacle)
                        if MainGame.game_level > 2:
                            object_obstacle = class_obstacle(MainGame.image_obstacle, object_skill.rect.x, -160)  # 障碍物
                            self.group_obstalce.add(object_obstacle)
                            if MainGame.game_level > 3:
                                object_obstacle = class_obstacle(MainGame.image_obstacle, object_skill.rect.x,100)  # 障碍物
                                self.group_obstalce.add(object_obstacle)

            elif event.type==CREATE_GOLD_EVENT:
                number_gold = random.randint(1, 5)  # 金币数量
                speed_glod = random.randint(2, 4)#金币速度
                max_x = SCREEN_RECT.width - 40 - GameSprite.wall_thick#40表示金币宽度
                min_x = GameSprite.wall_thick
                rect_x_glod = random.randint(min_x, max_x)
                for i in range(0,number_gold):
                    object_glod=class_glod(MainGame.image_glod,rect_x_glod,0-i*50,speed_glod)
                    self.group_glod.add(object_glod)

        # 使用键盘提供的方法获取键盘按键 - 按键元组
        keys_pressed = pygame.key.get_pressed()
        # 判断元组中对应的按键索引值 1
        if keys_pressed[pygame.K_SPACE]:  # 空格
            if MainGame.ninja.rect.left == GameSprite.wall_thick:
                MainGame.ninja.speed_x = 10
            elif MainGame.ninja.rect.right == SCREEN_RECT.width - GameSprite.wall_thick:
                MainGame.ninja.speed_x = -10
        else:
            pass
    def __check_collide(self):

        # 1.障碍物撞到英雄
        obstacles = pygame.sprite.spritecollide(MainGame.ninja, self.group_obstalce, True)

        # 判断列表时候有内容
        if len(obstacles) > 0:
            if MainGame.ninja.ninja_blood>0:
                if MainGame.skills_list[2]==1 and MainGame.skill_time[2]<=MainGame.skill_TIME:
                    pass#无敌不掉血
                else:
                    MainGame.ninja.ninja_blood-=1
                    if MainGame.ninja.ninja_blood==0:
                        MainGame.ninja.kill()
                        MainGame.__game_over()
            else:
                # 让忍者陨落
                MainGame.ninja.kill()
                # 结束游戏
                MainGame.__game_over()
        skills=pygame.sprite.spritecollide(MainGame.ninja, self.group_skill, True)
        if len(skills) > 0:
            for skill_i in skills:
                MainGame.skills_list[skill_i.skill_kind]=1
                MainGame.skill_time[skill_i.skill_kind]=0
                if skill_i.skill_kind==1:
                    MainGame.ninja.ninja_blood+=1

        glods=pygame.sprite.spritecollide(MainGame.ninja, self.group_glod, True)
        if len(glods)>0:
            MainGame.ninja.ninja_score+=10

    def __update_sprites(self):
        #背景图
        self.group_background.update()
        self.group_background.draw(MainGame.screen)
        #终点线
        if MainGame.ninja.ninja_score>MainGame.game_score[MainGame.game_level+1]:
            MainGame.game_level+=1
            level_finish=class_finish()
            self.group_finish.add(level_finish)
            #技能的最大速度
            class_skill.skill_speed_max=3+MainGame.game_level
            #障碍物最大速度
            class_obstacle.speed_obstacle_max=5+MainGame.game_level
        #画终点线
        self.group_finish.update()
        self.group_finish.draw(MainGame.screen)
        #障碍物
        self.group_obstalce.update()
        self.group_obstalce.draw(MainGame.screen)
        #忍者
        self.group_ninja.update()
        self.group_ninja.draw(MainGame.screen)
        if MainGame.skills_list[2]==1 and MainGame.skill_time[2]<=MainGame.skill_TIME:
            self.screen.blit(MainGame.image_skill[2], (MainGame.ninja.rect.x,MainGame.ninja.rect.y))
        if MainGame.skills_list[3]==1 and MainGame.skill_time[3]<=MainGame.skill_TIME:
            self.screen.blit(MainGame.image_skill[3], (MainGame.ninja.rect.x,MainGame.ninja.rect.y))
        #技能
        self.group_skill.update()
        self.group_skill.draw(MainGame.screen)
        #金币
        self.group_glod.update()
        self.group_glod.draw(MainGame.screen)
        #暂停键
        self.screen.blit(MainGame.Pause_button, (420,0))
        #得分
        font = pygame.font.SysFont("nsimsun", 40)  # 可以写成中文
        text_surface = font.render(str(MainGame.ninja.ninja_score), True, pygame.Color(255,0, 0), pygame.Color(255, 255, 255))#后边那个是背景颜色，白色
        self.screen.blit(text_surface, (0,SCREEN_RECT.height-40))
        #显示血量
        text_blood = font.render("血量："+str(MainGame.ninja.ninja_blood), True, pygame.Color(0, 255, 0), pygame.Color(0, 0, 130))
        self.screen.blit(text_blood, (SCREEN_RECT.right-160,SCREEN_RECT.bottom-40))
        #显示关卡
        text_blood = font.render("关卡：" + str(MainGame.game_level), True, pygame.Color(255, 0,0),
                                 pygame.Color(255, 255, 255))
        self.screen.blit(text_blood, (0,0))
    @staticmethod   #python staticmethod 返回函数的静态方法。
    # 该方法不强制要求传递参数，如下声明一个静态方法：
    def __game_over():
        print("游戏结束")
        print("最终得分：{}".format(MainGame.ninja.ninja_score))
        workbook = xlrd.open_workbook('历史数据.xls')
        sheet1 = workbook.sheet_by_name('Sheet1')
        nrows = sheet1.nrows
        wb = copy(workbook)
        sh1 = wb.get_sheet(0)
        sh1.write(nrows, 0, str(nrows))
        sh1.write(nrows, 1, str(MainGame.ninja.ninja_score))
        wb.save('历史数据.xls')
        pygame.quit()
        exit()

if __name__ == '__main__':
    # 创建游戏对象
    game = MainGame()
    # 启动游戏
    game.start_game()