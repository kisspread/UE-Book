# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、配置资产、管线节点） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

---

## 用途

MetaHuman Animator 是 Epic 官方的 MetaHuman 面部动画制作工具链。它解决的核心问题是：**如何从视频素材或音频中自动提取面部表情动画，并驱动 MetaHuman 角色的 Control Rig**。

整个插件围绕一条完整的面部动画生产管线构建：

1. **素材导入**（MetaHumanFootageIngest / MetaHumanCaptureSource）：导入深度视频、单目视频或音频作为输入源
2. **面部追踪**（MetaHumanFaceContourTracker / MeshTrackerInterface）：在视频帧中检测和追踪面部轮廓关键点
3. **面部拟合**（MetaHumanFaceFittingSolver）：将追踪结果拟合到 MetaHuman 面部网格
4. **动画求解**（MetaHumanFaceAnimationSolver）：将拟合结果转换为 Control Rig 控制值
5. **深度生成**（MetaHumanDepthGenerator）：从单目视频推断深度信息
6. **语音驱动**（MetaHumanSpeech2Face）：从音频直接生成面部动画
7. **性能资产**（MetaHumanPerformance）：作为管线的顶层容器，管理整个处理流程并导出动画序列
8. **批量处理**（MetaHumanBatchProcessor）：支持批量处理多个素材

与 MetaHuman Creator（负责角色创建）不同，MetaHuman Animator 专注于**动画制作**——让已创建的 MetaHuman 角色"活起来"。

## 使用场景

- 你有一段演员的面部表演视频（深度或单目），需要自动提取动画 → 使用 **Depth Footage** 或 **Monocular Footage** 输入模式
- 你只有音频文件，需要生成口型同步动画 → 使用 **Audio** 输入模式
- 你需要批量处理大量表演素材 → 使用 **MetaHumanBatchProcessor**
- 你需要将动画导出为 Sequencer 动画序列 → 使用 **MetaHumanPerformance** 的导出功能
- 你需要实时预览面部追踪效果 → 使用管线的 Preview 求解模式
- 你需要将动画适配到 Fortnite 角色 → 使用 Fortnite 兼容性设置

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTargetSkeleton` | 从 TargetSkeletonOrSkeletalMesh 获取目标 Skeleton 对象 | `UMetaHumanPerformanceExportAnimationSettings` |
| `IsTargetSkeletonCompatible` | 检查目标骨架是否包含所有必需的动画曲线，返回缺失的曲线列表 | `UMetaHumanPerformanceExportAnimationSettings` |

### 导出动画设置（UMetaHumanPerformanceExportAnimationSettings）

该类控制动画序列的导出行为，所有属性均可在蓝图中读写：

| 属性 | 类型 | 说明 |
|---|---|---|
| `bEnableHeadMovement` | bool | 是否在导出的动画中包含头部运动，默认 true |
| `bShowExportDialog` | bool | 是否显示导出对话框让用户选择保存位置，默认 true |
| `bAutoSaveAnimSequence` | bool | 是否自动保存生成的动画序列，默认 true |
| `ExportRange` | EPerformanceExportRange | 导出范围：ProcessingRange（仅处理范围）或 WholeSequence（整个序列） |
| `TargetSkeletonOrSkeletalMesh` | UObject* | 导出动画时使用的目标骨架或骨骼网格 |
| `CurveInterpolation` | ERichCurveInterpMode | 曲线关键帧之间的插值方式，默认线性插值 |
| `bRemoveRedundantKeys` | bool | 是否移除冗余关键帧，默认 true |
| `AssetName` | FString | 导出的关卡序列名称 |
| `PackagePath` | FString | 动画序列的保存路径 |

### 使用示例（蓝图描述）

**检查骨架兼容性**：
1. 创建 `UMetaHumanPerformanceExportAnimationSettings` 对象
2. 设置 `TargetSkeletonOrSkeletalMesh` 为你的目标骨架
3. 调用 `IsTargetSkeletonCompatible`，传入所需的曲线名称集合
4. 检查返回值和 `OutMissingCurvesInSkeleton` 数组，确认是否有缺失曲线

**配置导出设置**：
1. 创建 `UMetaHumanPerformanceExportAnimationSettings` 对象
2. 设置 `ExportRange` 为 `WholeSequence` 或 `ProcessingRange`
3. 设置 `bEnableHeadMovement` 控制是否包含头部运动
4. 设置 `CurveInterpolation` 选择插值模式
5. 将设置对象传递给导出函数

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanPerformance.h"
#include "MetaHumanPerformanceExportUtils.h"
```

### 基本用法

**创建和配置导出设置**：

```cpp
// 创建导出动画设置对象
UMetaHumanPerformanceExportAnimationSettings* ExportSettings = NewObject<UMetaHumanPerformanceExportAnimationSettings>();

// 配置导出参数
ExportSettings->bEnableHeadMovement = true;
ExportSettings->ExportRange = EPerformanceExportRange::WholeSequence;
ExportSettings->CurveInterpolation = ERichCurveInterpMode::RCIM_Linear;
ExportSettings->bRemoveRedundantKeys = true;
ExportSettings->bAutoSaveAnimSequence = true;
ExportSettings->bShowExportDialog = true;

// 设置目标骨架
ExportSettings->TargetSkeletonOrSkeletalMesh = YourSkeleton;

// 检查骨架兼容性
TSet<FString> RequiredCurves = { TEXT("CTRL_eyebrow_up_down"), TEXT("CTRL_mouth_smile") };
TArray<FString> MissingCurves;
bool bCompatible = ExportSettings->IsTargetSkeletonCompatible(RequiredCurves, MissingCurves);

if (!bCompatible)
{
    for (const FString& Curve : MissingCurves)
    {
        UE_LOG(LogTemp, Warning, TEXT("Missing curve: %s"), *Curve);
    }
}
```

### 进阶用法

**使用 Performance 资产进行处理管线**：

```cpp
// MetaHumanPerformance 是核心资产类，代表一个完整的面部动画处理任务
// 它管理从输入素材到输出动画的完整管线

// EDataInputType 定义了三种输入模式：
// - EDataInputType::DepthFootage  : 深度视频 + 身份信息 → 动画
// - EDataInputType::Audio         : 音频 → 动画（语音驱动）
// - EDataInputType::MonoFootage   : 单目视频 → 动画

// ESolveType 控制求解质量：
// - ESolveType::Preview           : 快速预览
// - ESolveType::Standard          : 标准质量
// - ESolveType::AdditionalTweakers: 附加微调器

// EPerformanceHeadMovementMode 控制头部运动方式：
// - TransformTrack  : 使用变换轨道移动骨骼网格（基于根骨骼枢轴点）
// - ControlRig      : 使用 Control Rig 的头部控制开关
// - Disabled        : 无头部运动
```

**导出 Level Sequence 设置**：

```cpp
// UMetaHumanPerformanceExportLevelSequenceSettings 用于导出为关卡序列
// 与动画序列导出类似，但输出格式为 Level Sequence
// 可以在 Sequencer 中进一步编辑和混合
```

## 模块架构

由于本插件包含 28 个模块，按功能域划分如下：

### 核心框架
| 模块 | 职责 |
|---|---|
| `MetaHumanCore` | 核心基础库，提供通用工具和类型定义 |
| `MetaHumanPipeline` | 处理管线框架，定义节点化处理流程 |
| `MetaHumanPlatform` | 平台抽象层 |
| `MetaHumanConfig` | 配置管理 |

### 素材采集与导入
| 模块 | 职责 |
|---|---|
| `MetaHumanCaptureSource` | 捕获源管理 |
| `MetaHumanCaptureProtocolStack` | 捕获协议栈实现 |
| `MetaHumanCaptureUtils` | 捕获工具函数 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器 |
| `MetaHumanFootageIngest` | 素材导入处理 |

### 面部追踪与求解
| 模块 | 职责 |
|---|---|
| `MetaHumanFaceContourTracker` | 面部轮廓追踪核心算法 |
| `MetaHumanFaceFittingSolver` | 面部拟合求解器 |
| `MetaHumanFaceAnimationSolver` | 面部动画求解器 |
| `MetaHumanDepthGenerator` | 深度信息生成（单目→深度） |
| `MeshTrackerInterface` | 网格追踪接口抽象 |

### 动画与输出
| 模块 | 职责 |
|---|---|
| `MetaHumanPerformance` | 性能资产，管线顶层容器与动画导出 |
| `MetaHumanSequencer` | Sequencer 集成 |
| `MetaHumanSpeech2Face` | 语音驱动面部动画 |
| `MetaHumanBatchProcessor` | 批量处理 |

### 身份与配置
| 模块 | 职责 |
|---|---|
| `MetaHumanIdentity` | MetaHuman 身份资产（面部网格、骨骼映射） |
| `MetaHumanToolkit` | 工具集 |

### 编辑器扩展
| 模块 | 职责 |
|---|---|
| `MetaHumanCoreEditor` | 核心编辑器扩展 |
| `MetaHumanConfigEditor` | 配置编辑器 |
| `MetaHumanIdentityEditor` | 身份资产编辑器 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器 |
| `MetaHumanFaceContourTrackerEditor` | 轮廓追踪编辑器 |
| `MetaHumanFaceFittingSolverEditor` | 拟合求解编辑器 |
| `MetaHumanFaceAnimationSolverEditor` | 动画求解编辑器 |

### 测试
| 模块 | 职责 |
|---|---|
| `MetaHumanControlsConversionTest` | 控制转换测试 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库（底层算法） |
| `ControlRigDeveloper` | Control Rig 开发者工具，用于驱动面部骨骼 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器接口 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器组件 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器组件 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格通用工具 |

## 维护状态

### 近期更新

```
- 6201ee5377e8 修复本地化构建警告，修正 "Suppress" 拼写错误
- 00def5c9075c [MHA] 修复动画序列导出中的变换错误
- 0ae62930adb8 防止在捕获数据包含无效帧率时分配 MetaHuman 性能捕获数据
```

### 维护评价

- **创建时间**：2024 年 2 月，约 1.4 年历史
- **更新频率**：近期有功能性 bug 修复（变换导出错误、帧率验证），表明仍在积极维护
- **维护状态**：**活跃维护中** — 作为 Epic 官方 MetaHuman 工具链的核心组件，持续获得更新
- **已知限制**：
  - 仅支持 Win64 和 Linux 平台
  - Fortnite 兼容性参数（`bFortniteCompatibility`）当前未暴露给用户，但默认启用
  - 深度处理模式需要深度摄像头素材，单目模式精度相对较低
- **推荐程度**：**强烈推荐** — 这是 Epic 官方的 MetaHuman 面部动画解决方案，是制作高质量 MetaHuman 角色动画的标准工具。如果你的项目使用 MetaHuman 角色，这个插件几乎是必需的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/)