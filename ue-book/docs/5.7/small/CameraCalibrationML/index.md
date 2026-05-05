# Camera Calibration Machine Learning

> Reference implementation of a machine learning approach to distortion calibration.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | 需手动启用（IsExperimentalVersion=true） |
| 包含内容 | true |
| 模块 | CameraCalibrationML (Editor) |
| 创建时间 | 2024-09-11 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibrationML) | |

## 用途

CameraCalibrationML 提供了一个基于**神经网络（iResNet）**的镜头畸变标定求解器，作为 UE5 内置 CameraCalibration 插件的附加求解器。

传统镜头标定使用 OpenCV 的多项式畸变模型（8 参数），但该方法在面对复杂畸变（如鱼眼镜头、变形镜头）时精度有限。本插件使用**可逆残差网络（Invertible ResNet, iResNet）**来学习更精确的畸变映射关系，并通过 ST Map 输出畸变/反畸变查找表。

**核心流程**：
1. 先用 OpenCV 标定获得初始畸变参数和相机外参
2. 用 OpenCV 结果预训练神经网络（让网络先学到大致的畸变形状）
3. 端到端联合优化神经网络畸变模型 + 相机内参/外参
4. 输出 ST Map（256×256），用于实时畸变校正

该插件的 C++ 层仅是一个空壳模块（`FDefaultModuleImpl`），全部标定逻辑由 Python（PyTorch）实现，通过 UE5 的嵌入式 Python 环境运行。

## 使用场景

- 你在做 **Virtual Production**（虚拟制片），需要精确标定物理摄像机的镜头畸变
- 你的镜头畸变比较复杂，OpenCV 的多项式模型拟合效果不够好
- 你需要生成高质量的 ST Map 用于实时合成中的畸变校正
- 你想在 UE5 的 CameraCalibration 编辑器工具中使用神经网络求解器

## 蓝图用法

本插件不暴露任何 BlueprintCallable 函数或属性。它的功能完全通过 CameraCalibration 插件的 **Lens Distortion Tool** UI 来使用——在该工具的求解器下拉列表中会出现 "Neural Network Solver" 选项。

### 编辑器使用流程

1. 启用插件后，在编辑器中打开 **Lens Distortion Tool**（属于 CameraCalibration 插件）
2. 准备标定图案（棋盘格）的 3D 坐标和对应的 2D 图像点
3. 在求解器选项中选择 **"Neural Network Solver"**
4. 执行标定，插件会自动完成 OpenCV 初始标定 → 神经网络优化 → 输出 ST Map
5. 输出的 ST Map 保存在项目的 Content 目录下（文件名格式：`STMap_MM-DD-YYYY_HH-MM-SS.exr`）

## C++ 用法

本插件的 C++ 代码仅包含一个模块注册存根，没有可调用的 C++ API。所有功能通过 Python 实现。

### 模块注册

```cpp
// CameraCalibrationMLModule.cpp - 仅此一个文件
#include "Modules/ModuleManager.h"
IMPLEMENT_MODULE(FDefaultModuleImpl, CameraCalibrationML);
```

### Python 侧核心类

虽然不是 C++ API，但以下 Python 类是该插件的核心接口：

#### NeuralLensDistortionSolver（求解器入口）

在 `init_unreal.py` 中通过 `@unreal.uclass()` 注册为 UE 的 `LensDistortionSolver` 子类：

```python
@unreal.uclass()
class NeuralLensDistortionSolver(unreal.LensDistortionSolver):
    @unreal.ufunction(override=True)
    def solve(self, object_points_array, image_points_array, image_size,
              focal_length, image_center, init_distortion, camera_poses,
              target_poses, lens_model, pixel_aspect, solver_flags):
        return calibration.solve(self, object_points_array, ...)

    @unreal.ufunction(override=True)
    def get_display_name(self):
        return unreal.Text("Neural Network Solver")

    @unreal.ufunction(override=True)
    def is_enabled(self):
        return calibration.is_enabled()
```

#### NeuralLensDistortion（神经网络畸变模型）

定义在 `distortion.py`，基于 FrEIA 库的 iResNet 架构：

```python
from distortion import NeuralLensDistortion

# 创建模型：2 个 iResNet 节点，内部宽度 1024，2 层内部网络
model = NeuralLensDistortion(
    num_nodes=2,
    internal_size=1024,
    num_internal_layers=2,
    inp_size_linear=2,
)

# 前向 = 畸变，反向 = 反畸变（iResNet 的特性）
distorted = model.forward(uv, sensor_to_frustum=False)   # 畸变
undistorted = model.forward(uv, sensor_to_frustum=True)   # 反畸变

# 生成 ST Map
st_map = model.st_map(
    stmap_resolution=(256, 256),
    image_resolution=(1920, 1080),
    intrinsics=(fx, fy),
)
```

#### OpenCV8ParamDistortion（传统畸变模型）

同样定义在 `distortion.py`，用于预训练阶段：

```python
from distortion import OpenCV8ParamDistortion

# OpenCV 8 参数畸变（k1, k2, p1, p2, k3, k4, k5, k6）
cv_distortion = OpenCV8ParamDistortion(params=[-0.28, 0.07, 0, 0, 0, 0, 0, 0])
```

## Demo 示例

### 离线标定（CLI 模式）

`calibration.py` 支持在 UE5 外独立运行，方便调试：

```bash
# 准备 JSON 格式的标定数据
# {
#   "board_coordinates_xyz": [...],
#   "frame_coordinates_xy": [...],
#   "resolution_wh": [1920, 1080],
#   "focal_length": [1000, 1000],
#   "image_center": [960, 540]
# }

python calibration.py calibration_data.json
# 输出：rmse、焦距、主点、stmap.exr
```

### Build.cs 依赖

若要从自己的 Editor 模块中调用此插件的功能，需要在 `Build.cs` 中添加：

```csharp
PrivateDependencyModuleNames.AddRange(new string[] {
    "CameraCalibrationEditor",
    "Core",
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CameraCalibrationEditor` | CameraCalibration 编辑器工具，提供 LensDistortionSolver 基类 |
| `Core` | UE5 核心模块 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `CameraCalibration` | 提供镜头标定框架、LensDistortionSolver 基类、编辑器 UI |
| `PythonMLPackages` | 提供 PyTorch 等 Python ML 包的运行环境 |

### Python 依赖（随插件分发）

| 包 | 版本 | 用途 |
|---|---|---|
| PyTorch | - | 深度学习框架，神经网络训练和推理 |
| FrEIA | v0.2 | 可逆神经网络框架，提供 iResNet 架构 |
| nerfacc | 0.5.3 | 提供 OpenCV 镜头畸变/反畸变的 PyTorch 实现 |
| BARF | - | 提供 SE3/se3 李群/李代数转换（相机姿态优化） |
| OpenCV | - | 传统标定、图像 IO（ST Map 写入 EXR） |
| NumPy | - | 数值计算 |
| SciPy | - | 矩阵平方根（预条件矩阵计算） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 将 PyTorch 依赖拆分到独立的 PythonMLPackages 插件，本插件变为依赖它而非自带 |
| 2024-09-11 | `08a49766` | CameraCalibration: Move ML python scripts into dedicated plugin to isolate pytorch dependency | 初始提交——从 CameraCalibration 插件中拆分出 ML 部分，创建独立插件 |

### 维护评价

- **创建时间**：2024-09-11，不到 2 年，属于较新的插件
- **更新频率**：仅 2 次提交，均为结构性调整（拆分/重组），没有功能性更新
- **实验性标记**：`IsExperimentalVersion=true`，尚未正式发布
- **活跃度**：维护不活跃，代码中有多个 TODO 注释表明仍处于开发中
- **已知限制**：
  - 硬编码使用 CUDA（`device_name = "cuda"`），不支持 CPU 推理
  - 训练参数（epoch 数、学习率等）大部分硬编码
  - ST Map 分辨率硬编码为 256×256
  - 无自动化测试
- **推荐**：仅推荐在 Virtual Production 实验性工作流中使用，不建议用于生产环境

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibrationML)
- 官方文档（无）
- [CameraCalibration 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibration) — 本插件的宿主框架
- [FrEIA 库](https://github.com/vislearn/FrEIA) — 可逆神经网络框架
- [nerfacc](https://github.com/nerfstudio-project/nerfacc) — OpenCV 畸变实现来源
- [BARF](https://github.com/chenhsuanlin/bundle-adjusting-nerf) — 李群/李代数旋转工具
