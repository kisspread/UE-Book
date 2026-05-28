# MetaHuman Animator Calibration Processing

> The official MetaHuman Calibration Processing Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 标定处理 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MetaHumanCalibrationCore` (Runtime), `MetaHumanCalibrationGenerator` (Runtime), `MetaHumanCalibrationLib` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing) | |

## 用途

MetaHumanCalibrationProcessing 是 MetaHuman Animator 工作流中的相机标定处理引擎。它实现了完整的多视角几何（Multiple-View-Geometry）标定管线，用于精确校准多相机系统。

该插件解决的核心问题：在 MetaHuman Animator 的面部捕捉流程中，需要使用多个相机同时拍摄棋盘格标定板来计算每个相机的内参（焦距、主点、畸变）和外参（旋转、平移），从而将多个相机的 2D 图像投射到统一的 3D 坐标系中。这一步是面部动画捕捉的前置条件——只有完成标定，才能进行后续的面部追踪和驱动。

底层基于 Epic 的 Titan 引擎（v9.0.8），包含：
- **calib**：核心标定库，实现 Zhang 标定法、棋盘格检测、内外参标定、束调整（Bundle Adjustment）
- **carbon**：基础设施库，提供几何数据结构（AABB 树、Kd 树）、JSON I/O、SIMD 加速、NPY 文件格式
- **nls**：非线性最小二乘求解器，支持自动微分（DiffScalar/Jacobian）、PCG 线性求解器、顶点优化
- **rig**：骨骼绑定几何体（BodyGeometry、RigGeometry、RigLogic），用于 MetaHuman 角色的关节驱动和蒙皮

## 使用场景

- 你在使用 **MetaHuman Animator** 进行面部捕捉 → 需要先完成多相机标定才能进行面部驱动
- 你有一个 **多相机拍摄系统** 需要标定相机内参和外参 → 使用 CalibContext API
- 你需要检测图像中的 **棋盘格标定图案** → 使用 detectPattern / detectMultiplePatterns
- 你需要进行 **立体相机标定**（stereo calibration）→ 使用 calibrateStereoExtrinsics
- 你需要将 2D 投影点 **三角化** 为 3D 坐标 → 使用 triangulatePoints
- 你需要在打包后的运行时进行标定计算 → 三个模块均为 Runtime 类型

## 蓝图用法

该插件的所有模块均为 Runtime 类型，核心标定库（calib）为纯 C++ 实现。从源码分析来看，`MetaHumanCalibrationLib` 模块依赖 `UnrealEd`，但提供的标定 API 主要面向 C++ 开发者。

该插件的公开蓝图 API 信息需进一步查看 `MetaHumanCalibrationGenerator` 模块（本分析聚焦于 `MetaHumanCalibrationLib`）。

## C++ 用法

### 头文件引入

```cpp
// 核心标定上下文
#include "calib/CalibContext.h"

// 相机模型和相机
#include "calib/CameraModel.h"

// 标定函数
#include "calib/Calibration.h"

// 标定对象（棋盘格）
#include "calib/Object.h"

// 工具函数
#include "calib/Utilities.h"
```

### 基本用法：创建标定场景并标定

从 `CalibContext.h` 提取的典型标定流程：

```cpp
#include "calib/CalibContext.h"
#include "calib/Calibration.h"

using namespace TITAN_NAMESPACE::calib;

// 1. 创建标定上下文
auto contextOpt = CalibContext::create();
if (!contextOpt) return;
CalibContext* context = *contextOpt;

// 2. 设置标定类型（完整标定、固定内参、固定投影）
context->setCalibrationType(SceneCalibrationType::FULL_CALIBRATION);

// 3. 设置棋盘格检测算法（快速 / 深度检测）
context->setPatternDetectorType(PatternDetect::DETECT_DEEP);

// 4. 添加标定物体（棋盘格）: 9x6 方格，每格 25mm
auto planeOpt = context->addObjectPlane(9, 6, 0.025f);
if (!planeOpt) return;
ObjectPlane* plane = *planeOpt;

// 5. 添加相机模型（指定图像分辨率）
auto modelOpt = context->addCameraModel("cam1", 1920, 1080);
if (!modelOpt) return;
CameraModel* camModel = *modelOpt;

// 6. 添加相机
auto camOpt = context->addCamera("cam1", /*modelIndex=*/0);
if (!camOpt) return;
Camera* camera = *camOpt;

// 7. 添加标定图像
auto imgOpt = context->addImage(
    "/path/to/calib_image.png",  // 图像路径
    "cam1",                       // 相机模型名
    "cam1",                       // 相机名
    0,                            // 帧 ID
    ImageLoadType::LOAD_PROXY     // 加载方式
);

// 8. 设置束调整参数
BAParams baParams;
baParams.iterations = 100;
baParams.optimizeIntrinsics = true;
baParams.optimizeDistortion = true;
context->setBundleAdjustOptimParams(baParams);

// 9. 执行标定！
bool success = context->calibrateScene();

// 10. 获取重投影误差
real_t mse = context->getMse();
```

*来源：`Private/calib/include/calib/CalibContext.h`*

### 基本用法：检测棋盘格图案

```cpp
#include "calib/Calibration.h"

using namespace TITAN_NAMESPACE::calib;

// 加载图像
auto imageOpt = loadImage("/path/to/image.png");
if (!imageOpt) return;

// 检测单个棋盘格图案
auto pointsOpt = detectPattern(
    *imageOpt,        // 图像矩阵（灰度）
    9,                // 宽度方向方格数
    6,                // 高度方向方格数
    0.025f,           // 方格边长
    PatternDetect::DETECT_DEEP  // 检测算法
);

if (pointsOpt) {
    // *pointsOpt 是 (N, 2) 矩阵，包含检测到的棋盘格角点
    const Eigen::MatrixX<real_t>& corners = *pointsOpt;
    // ...
}

// 检测多个棋盘格图案
std::vector<Eigen::MatrixX<real_t>> multiPoints = detectMultiplePatterns(
    *imageOpt,
    {9, 9},           // 每个图案的宽度
    {6, 6},           // 每个图案的高度
    {0.025f, 0.05f},  // 每个图案的方格大小
    PatternDetect::DETECT_FAST
);
```

*来源：`Private/calib/include/calib/Calibration.h`*

### 进阶用法：相机内参和外参标定

```cpp
#include "calib/Calibration.h"

using namespace TITAN_NAMESPACE::calib;

// --- 内参标定 ---
// 准备多视角的 2D-3D 对应点
std::vector<Eigen::MatrixX<real_t>> points2d; // 各视角的 2D 投影点
std::vector<Eigen::MatrixX<real_t>> points3d; // 对应的 3D 世界坐标点
Eigen::Matrix3<real_t> intrinsics = Eigen::Matrix3<real_t>::Identity();
Eigen::VectorX<real_t> distortion(5);

// 标定内参（同时估计 K 矩阵和径向畸变）
auto mseOpt = calibrateIntrinsics(
    points2d, points3d,
    intrinsics, distortion,
    1920, 1080,
    IntrinsicEstimation::K_AND_D  // 同时估计 K 和 D
);

// --- 外参标定 ---
Eigen::Matrix4<real_t> T; // 输出的 4x4 变换矩阵 [R|t]
auto mseExOpt = calibrateExtrinsics(
    detected2d, detected3d,
    intrinsics, distortion, T
);

// --- 立体相机标定 ---
Eigen::Matrix4<real_t> stereoT;
auto mseStereo = calibrateStereoExtrinsics(
    points2d_cam1, points2d_cam2, points3d,
    intrinsics_1, intrinsics_2,
    distortion_1, distortion_2,
    stereoT, 1920, 1080
);
```

*来源：`Private/calib/include/calib/Calibration.h`*

### 进阶用法：使用 CameraModel 类

```cpp
#include "calib/CameraModel.h"

using namespace TITAN_NAMESPACE::calib;

// 创建相机模型
auto modelOpt = CameraModel::create("main_cam", 1920, 1080);
if (!modelOpt) return;
CameraModel* model = *modelOpt;

// 设置预计算的投影数据
model->setProjectionData(projections);

// 标定内参
auto mseOpt = model->calibrateIntrinsics();

// 获取结果
const Eigen::Matrix3<real_t>& K = model->getIntrinsicMatrix();
const Eigen::VectorX<real_t>& D = model->getDistortionParams();

// 创建相机并标定外参
auto camOpt = Camera::create("cam1", model);
if (!camOpt) return;
Camera* camera = *camOpt;

camera->calibrateExtrinsics();

// 获取相机世界位置
const Eigen::Matrix4<real_t>& worldPos = camera->getWorldPosition();

// 使用智能指针自动析构
std::unique_ptr<CameraModel, CameraModel::destructor> safeModel(model);
std::unique_ptr<Camera, Camera::destructor> safeCam(camera);
```

*来源：`Private/calib/include/calib/CameraModel.h`*

### 进阶用法：几何工具函数

```cpp
#include "calib/Utilities.h"

using namespace TITAN_NAMESPACE::calib;

// 分离旋转和平移
Eigen::Matrix3<real_t> R;
Eigen::Vector3<real_t> t;
splitRotationAndTranslation(transform4x4, R, t);

// 构造变换矩阵
Eigen::Matrix4<real_t> T = makeTransformationMatrix(R, t);

// 四元数与旋转矩阵互转
Eigen::Vector4<real_t> q = rotationMatrixToQuaternion(R);
Eigen::Matrix3<real_t> R2 = quaternionToRotationMatrix(q);

// 三角化
std::optional<Eigen::MatrixX<real_t>> pt3d = triangulatePoints(
    p2d_cam1, p2d_cam2,
    K1, K2, T1, T2
);

// 计算重投影误差
std::optional<real_t> mse = calculateMeanSquaredError(lhs, rhs);
```

*来源：`Private/calib/include/calib/Utilities.h`*

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | MetaHumanCalibrationLib 依赖编辑器功能 |
| Eigen | 线性代数库（矩阵运算、SVD 分解等） |
| OpenCV | 图像处理和棋盘格检测（通过 AfterOpenCvHeaders.h） |

## 模块结构

| 模块 | 类型 | 说明 |
|---|---|---|
| `MetaHumanCalibrationCore` | Runtime | 核心标定数据结构和处理逻辑 |
| `MetaHumanCalibrationGenerator` | Runtime | 标定资产生成器 |
| `MetaHumanCalibrationLib` | Runtime | 底层标定库（含 calib/carbon/nls/rig 子库） |

### MetaHumanCalibrationLib 内部子库

| 子库 | 路径 | 说明 |
|---|---|---|
| **calib** | `Private/calib/` | 核心标定算法（Zhang 标定法、束调整） |
| **carbon** | `Private/carbon/` | 基础设施（几何体、JSON I/O、SIMD、NPY 格式） |
| **nls** | `Private/nls/` | 非线性最小二乘求解器（自动微分、PCG、顶点优化） |
| **rig** | `Private/rig/` | 骨骼绑定几何体（BodyGeometry、RigLogic、RBF 求解器） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | 升级 Titan 引擎至 v9.0.8 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | 升级 Titan 引擎至 v9.0.7 |
| 2026-05-21 | `e936df4b` | [MetaHuman] Titan v9.0.6 | 升级 Titan 引擎至 v9.0.6 |
| 2026-05-14 | `52cbd20d` | [MetaHuman] titan v9.0.5 | 升级 Titan 引擎至 v9.0.5 |
| 2026-05-13 | `df646fb2` | Use infinity as limit for initial distance, to not overflow float in calculations | 修复浮点溢出问题，使用无穷大作为初始距离限制 |

### 维护评价

- **创建时间**：2025-04-01，约 1 年历史，属于较新的插件
- **更新频率**：最近一个月内有 5 次提交，主要是 Titan 引擎版本升级和 bug 修复，**非常活跃**
- **维护状态**：活跃维护中。作为 MetaHuman 工具链的核心组件，Epic 持续迭代
- **已知限制**：
  - `MetaHumanCalibrationLib` 依赖 `UnrealEd`，意味着不能在纯打包项目中使用
  - 标定 API 为纯 C++，无蓝图接口
  - 代码中有大量 `TODO` 注释（如 `CALIB_API TODO this is the core module which is a static library`），API 可能还在演化中
- **推荐使用**：如果你在使用 MetaHuman Animator 进行面部捕捉，这是必经的标定步骤。对于独立的相机标定需求，可直接使用底层的 calib 子库 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing)
- [官方文档]()（暂无）