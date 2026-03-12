# 因果模型：在线Mini-Batch KMeans状态映射（自适应工业场景）
# behavior_gene/causal_model.py

from sklearn.cluster import MiniBatchKMeans
import numpy as np
from typing import List, Optional

class AdaptiveStateMapper:
    """自适应状态映射器：基于在线聚类实现工业设备状态自动划分"""
    def __init__(self, n_clusters: int = 4, random_state: int = 0):
        self.kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=random_state, batch_size=100)
        self.history: List[np.ndarray] = []  # 特征历史数据
        self.is_fitted: bool = False  # 模型是否完成拟合
        self.n_clusters = n_clusters

    def partial_fit(self, features: np.ndarray) -> None:
        """在线拟合：积累特征，每100个样本更新一次聚类中心"""
        # 特征维度校验（需为1D数组）
        if len(features.shape) != 1:
            raise ValueError("特征必须为一维数组")
        
        self.history.append(features)
        # 每积累100个样本，使用最近500个样本更新模型
        if len(self.history) >= 100:
            X = np.array(self.history[-500:])  # 取最近500个样本，防止过拟合
            self.kmeans.partial_fit(X)
            self.is_fitted = True
            # 清理历史数据（可选，节省内存）
            if len(self.history) > 1000:
                self.history = self.history[-500:]

    def map(self, features: np.ndarray) -> int:
        """状态映射：输入特征，输出聚类后的状态编号"""
        if not self.is_fitted:
            return 0  # 模型未拟合时，返回默认状态0
        
        if len(features.shape) != 1:
            raise ValueError("特征必须为一维数组")
        
        # 预测状态编号（0~n_clusters-1）
        state = self.kmeans.predict(features.reshape(1, -1))[0]
        return int(state)

# 因果模型主类
class CausalBehaviorModel:
    def __init__(self):
        self.state_mapper = AdaptiveStateMapper(n_clusters=4)  # 初始化状态映射器

    def update_state(self, features: np.ndarray) -> int:
        """更新设备状态：先拟合特征，再映射状态"""
        self.state_mapper.partial_fit(features)
        return self.state_mapper.map(features)

# 测试示例
if __name__ == "__main__":
    model = CausalBehaviorModel()
    # 模拟100组工业设备特征（5维特征：温度、压力、转速、电压、电流）
    for i in range(120):
        features = np.random.rand(5) * 100  # 随机生成特征
        state = model.update_state(features)
        if i % 20 == 0:
            print(f"第{i}组特征，设备状态：{state}，模型已拟合：{model.state_mapper.is_fitted}")