"""
炉石战棋识别引擎
基于OpenCV模板匹配的图像识别模块
"""

import cv2
import numpy as np
import os
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MatchResult:
    """模板匹配结果"""
    template_id: str
    confidence: float
    position: Tuple[int, int]
    size: Tuple[int, int]


@dataclass
class MinionInfo:
    """随从信息"""
    position: int
    name: str
    attack: int
    health: int
    tier: int
    tribe: str
    golden: bool
    divine_shield: bool = False
    reborn: bool = False


@dataclass
class HeroInfo:
    """英雄信息"""
    name: str
    health: int
    armor: int


@dataclass
class GameState:
    """游戏状态"""
    timestamp: str
    tavern_tier: int
    gold: int
    turn: int
    hero: HeroInfo
    shop: Dict
    board: Dict


class TemplateManager:
    """模板资源管理器"""
    
    def __init__(self, template_dir: str = "static/media"):
        self.template_dir = Path(template_dir)
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """加载所有模板图片"""
        # 加载英雄模板
        heroes_dir = self.template_dir / "heroes"
        if heroes_dir.exists():
            for hero_file in heroes_dir.glob("*.png"):
                hero_name = hero_file.stem
                template = cv2.imread(str(hero_file))
                if template is not None:
                    self.templates[f"hero_{hero_name}"] = template
        
        # 加载随从模板
        minions_dir = self.template_dir / "minions"
        if minions_dir.exists():
            for minion_file in minions_dir.glob("*.png"):
                minion_name = minion_file.stem
                template = cv2.imread(str(minion_file))
                if template is not None:
                    self.templates[f"minion_{minion_name}"] = template
    
    def get_template(self, template_id: str) -> Optional[np.ndarray]:
        """获取指定模板"""
        return self.templates.get(template_id)


class RecognitionEngine:
    """识别引擎主类"""
    
    def __init__(self):
        self.template_manager = TemplateManager()
        self.minions_data = self.load_minions_data()
        self.heroes_data = self.load_heroes_data()
        
        # 游戏界面ROI定义（基于1920x1080分辨率）
        self.rois = {
            "shop": (400, 200, 800, 400),      # 商店区域
            "board": (400, 600, 800, 300),     # 我方场面
            "hero": (100, 800, 200, 200),      # 英雄区域
            "gold": (1600, 800, 100, 50),      # 金币区域
            "tavern_tier": (1600, 700, 100, 50), # 酒馆等级
            "turn": (1600, 600, 100, 50),      # 回合数
        }
    
    def load_minions_data(self) -> Dict:
        """加载随从数据"""
        try:
            with open("data/bgs/minions.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def load_heroes_data(self) -> Dict:
        """加载英雄数据"""
        try:
            with open("data/bgs/heroes.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def extract_roi(self, frame: np.ndarray, roi_name: str) -> np.ndarray:
        """提取指定ROI区域"""
        x, y, w, h = self.rois[roi_name]
        return frame[y:y+h, x:x+w]
    
    def template_match(self, roi: np.ndarray, template_id: str, 
                      threshold: float = 0.7) -> Optional[MatchResult]:
        """模板匹配"""
        template = self.template_manager.get_template(template_id)
        if template is None:
            return None
        
        # 多尺度模板匹配
        scales = [0.8, 0.9, 1.0, 1.1, 1.2]
        best_match = None
        best_confidence = 0
        
        for scale in scales:
            # 缩放模板
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            if width <= 0 or height <= 0:
                continue
            
            resized_template = cv2.resize(template, (width, height))
            
            # 模板匹配
            result = cv2.matchTemplate(roi, resized_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence and max_val > threshold:
                best_confidence = max_val
                best_match = MatchResult(
                    template_id=template_id,
                    confidence=max_val,
                    position=max_loc,
                    size=(width, height)
                )
        
        return best_match
    
    def recognize_minions(self, shop_roi: np.ndarray) -> List[MinionInfo]:
        """识别商店随从"""
        minions = []
        
        # 简单的网格分割（假设7个随从位置）
        shop_height, shop_width = shop_roi.shape[:2]
        card_width = shop_width // 7
        
        for i in range(7):
            x = i * card_width
            card_roi = shop_roi[:, x:x+card_width]
            
            # 尝试匹配所有随从模板
            best_match = None
            best_confidence = 0
            
            for template_id in self.template_manager.templates:
                if template_id.startswith("minion_"):
                    match = self.template_match(card_roi, template_id, threshold=0.6)
                    if match and match.confidence > best_confidence:
                        best_confidence = match.confidence
                        best_match = match
            
            if best_match:
                minion_name = best_match.template_id.replace("minion_", "")
                # 从数据中查找随从信息
                minion_info = self.get_minion_info(minion_name)
                if minion_info:
                    minions.append(MinionInfo(
                        position=i,
                        name=minion_name,
                        attack=minion_info.get("attack", 0),
                        health=minion_info.get("health", 0),
                        tier=minion_info.get("tier", 0),
                        tribe=minion_info.get("tribe", ""),
                        golden=False  # 暂时不识别金卡
                    ))
        
        return minions
    
    def get_minion_info(self, minion_name: str) -> Optional[Dict]:
        """获取随从详细信息"""
        for minion in self.minions_data:
            if minion.get("name", "").lower() == minion_name.lower():
                return minion
        return None
    
    def recognize_hero(self, hero_roi: np.ndarray) -> Optional[HeroInfo]:
        """识别英雄"""
        best_match = None
        best_confidence = 0
        
        for template_id in self.template_manager.templates:
            if template_id.startswith("hero_"):
                match = self.template_match(hero_roi, template_id, threshold=0.6)
                if match and match.confidence > best_confidence:
                    best_confidence = match.confidence
                    best_match = match
        
        if best_match:
            hero_name = best_match.template_id.replace("hero_", "")
            # 从数据中查找英雄信息
            hero_info = self.get_hero_info(hero_name)
            if hero_info:
                return HeroInfo(
                    name=hero_name,
                    health=30,  # 暂时使用默认值
                    armor=0
                )
        
        return None
    
    def get_hero_info(self, hero_name: str) -> Optional[Dict]:
        """获取英雄详细信息"""
        for hero in self.heroes_data:
            if hero.get("name", "").lower() == hero_name.lower():
                return hero
        return None
    
    def recognize_frame(self, frame: np.ndarray) -> GameState:
        """识别单帧图像，返回游戏状态"""
        import datetime
        
        # 提取各个ROI
        shop_roi = self.extract_roi(frame, "shop")
        board_roi = self.extract_roi(frame, "board")
        hero_roi = self.extract_roi(frame, "hero")
        
        # 识别各个部分
        shop_minions = self.recognize_minions(shop_roi)
        board_minions = self.recognize_minions(board_roi)  # 暂时复用商店识别逻辑
        hero = self.recognize_hero(hero_roi)
        
        # 构建游戏状态
        game_state = GameState(
            timestamp=datetime.datetime.now().isoformat(),
            tavern_tier=6,  # 暂时使用默认值
            gold=10,        # 暂时使用默认值
            turn=1,         # 暂时使用默认值
            hero=hero or HeroInfo(name="Unknown", health=30, armor=0),
            shop={
                "frozen": False,
                "minions": [vars(m) for m in shop_minions]
            },
            board={
                "minions": [vars(m) for m in board_minions]
            }
        )
        
        return game_state


# 测试代码
if __name__ == "__main__":
    engine = RecognitionEngine()
    print(f"加载了 {len(engine.template_manager.templates)} 个模板")
    print(f"加载了 {len(engine.minions_data)} 个随从数据")
    print(f"加载了 {len(engine.heroes_data)} 个英雄数据")
