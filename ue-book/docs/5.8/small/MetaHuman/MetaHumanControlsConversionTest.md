# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、捕获数据模板、动画蓝图） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | ~2022 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

---

> **⚠️ 超大型插件（xlarge，544 源文件）**：本文档为汇总索引页，涵盖插件整体架构与核心模块概述。当前文件分析聚焦于 `MetaHumanControlsConversionTest` 测试模块。

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色面部动画全流程工具链。它解决的核心问题是：**将真实世界的人脸捕捉数据（视频/深度/性能捕捉）转换为 MetaHuman 角色的面部动画驱动数据**。

整个插件由 28 个模块组成，覆盖从底层数据捕获到高层动画输出的完整流水线：

- **捕获与导入**：通过专有协议栈接收面部捕捉设备数据，支持多种输入源（iPhone LiDAR、视频素材等）
- **面部处理流水线**：轮廓追踪（Contour Tracking）→ 深度生成（Depth Generation）→ 面部拟合（Face Fitting）→ 动画求解（Animation Solving），逐步将原始捕捉数据转化为高质量面部动画
- **身份系统（Identity）**：管理和维护 MetaHuman 角色的面部身份信息，与 Control Rig 深度集成
- **语音驱动**：Speech2Face 模块可从音频直接生成面部动画
- **序列器集成**：在 Sequencer 中直接编辑和回放 MetaHuman 动画
- **批处理**：支持批量处理大量捕捉素材

`MetaHumanControlsConversionTest` 模块是一个内部测试模块，专门用于验证**面部控制参数在不同格式之间的转换正确性**——即将 Animation Solver 输出的求解控制（Solve Controls，如 `CTRL_L_brow_down.ty`）正确映射为 MetaHuman Rig 控制（Rig Controls，如 `CTRL_expressions_browDownL`）。

## 模块架构

### 核心基础设施

| 模块 | 说明 |
|---|---|
| `MetaHumanCore` | 核心运行时功能，公共基础类 |
| `MetaHumanCoreEditor` | 编辑器核心扩展 |
| `MetaHumanToolkit` | 工具集公共组件 |
| `MetaHumanConfig` | 配置管理（依赖 MetaHumanCoreTechLib） |
| `MetaHumanConfigEditor` | 配置编辑器 |
| `MetaHumanPlatform` | 平台抽象层 |

### 捕获与导入

| 模块 | 说明 |
|---|---|
| `MeshTrackerInterface` | 网格追踪设备接口抽象 |
| `MetaHumanCaptureProtocolStack` | 捕获协议栈（设备通信协议实现） |
| `MetaHumanCaptureSource` | 捕获数据源管理 |
| `MetaHumanCaptureUtils` | 捕获工具函数库 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器 |
| `MetaHumanFootageIngest` | 视频素材导入处理 |
| `MetaHumanImageViewerEditor` | 图像查看编辑器 |

### 面部处理流水线

| 模块 | 说明 |
|---|---|
| `MetaHumanFaceContourTracker` | 面部轮廓追踪算法 |
| `MetaHumanFaceContourTrackerEditor` | 轮廓追踪编辑器工具 |
| `MetaHumanDepthGenerator` | 从 2D 捕获生成深度信息 |
| `MetaHumanFaceFittingSolver` | 面部网格拟合求解器 |
| `MetaHumanFaceFittingSolverEditor` | 面部拟合编辑器工具 |
| `MetaHumanFaceAnimationSolver` | 面部动画求解器（核心算法） |
| `MetaHumanFaceAnimationSolverEditor` | 动画求解编辑器工具 |
| `MetaHumanSpeech2Face` | 语音驱动面部动画 |

### 身份与角色

| 模块 | 说明 |
|---|---|
| `MetaHumanIdentity` | MetaHuman 身份系统（依赖 ControlRigDeveloper） |
| `MetaHumanIdentityEditor` | 身份编辑器 |

### 动画与流水线

| 模块 | 说明 |
|---|---|
| `MetaHumanPerformance` | 性能捕捉动画资产 |
| `MetaHumanSequencer` | Sequencer 集成（动画编辑/回放） |
| `MetaHumanPipeline` | 处理流水线管理 |
| `MetaHumanBatchProcessor` | 批量处理 |

### 测试

| 模块 | 说明 |
|---|---|
| `MetaHumanControlsConversionTest` | 控制参数转换验证测试（当前分析模块） |

## 使用场景

- **你需要将 iPhone 面部捕捉数据驱动 MetaHuman 角色** → 使用 MetaHuman Animator 的捕获流水线
- **你需要从视频素材生成 MetaHuman 面部动画** → 使用 MetaHumanFootageIngest + FaceAnimationSolver
- **你需要用语音驱动 MetaHuman 嘴部动画** → 使用 MetaHumanSpeech2Face
- **你需要在 Sequencer 中编辑 MetaHuman 面部动画关键帧** → 使用 MetaHumanSequencer
- **你需要批量处理大量捕捉素材** → 使用 MetaHumanBatchProcessor
- **你需要验证面部控制参数的转换正确性** → 参考 MetaHumanControlsConversionTest 的测试用例

## 面部控制参数命名规范

从测试数据 `MetaHumanControlsConversionTest` 可以提取出 MetaHuman 面部动画的两套控制命名规范：

### Solve Controls（求解器输出格式）

面部求解器输出的控制参数，带轴向后缀：

```
CTRL_{L/R/C}_{区域}_{动作}.{轴向}
```

| 区域 | 示例 |
|---|---|
| 眉毛 | `CTRL_L_brow_down.ty`, `CTRL_R_brow_raiseIn.ty` |
| 眼睛 | `CTRL_L_eye_blink.ty`, `CTRL_R_eye_squintInner.ty` |
| 鼻子 | `CTRL_L_nose.ty`, `CTRL_R_nose_nasolabialDeepen.ty` |
| 嘴部 | `CTRL_L_mouth_cornerPull.ty`, `CTRL_C_mouth.tx` |
| 下巴 | `CTRL_C_jaw.ty`, `CTRL_C_jaw.tx` |
| 舌头 | `CTRL_C_tongue_move.ty`, `CTRL_C_tongue_tipMove.tx` |

- `L` = 左侧, `R` = 右侧, `C` = 中央
- `.ty` = Y轴平移, `.tx` = X轴平移

### Rig Controls（最终 Rig 格式）

转换后的 MetaHuman Rig 控制参数，无轴向后缀：

```
CTRL_expressions_{动作}{位置}
```

| 分类 | 示例 |
|---|---|
| 眉毛 | `CTRL_expressions_browDownL`, `CTRL_expressions_browRaiseInR` |
| 眼睛 | `CTRL_expressions_eyeBlinkL`, `CTRL_expressions_eyeSquintInnerR` |
| 下巴 | `CTRL_expressions_jawOpen`, `CTRL_expressions_jawLeft` |
| 嘴部 | `CTRL_expressions_mouthCornerPullL`, `CTRL_expressions_mouthDimpleR` |
| 舌头 | `CTRL_expressions_tongueUp`, `CTRL_expressions_tonguePress` |
| 鼻子 | `CTRL_expressions_noseNostrilDilateL`, `CTRL_expressions_noseWrinkleR` |
| 颈部 | `CTRL_expressions_neckDigastricDown`, `CTRL_expressions_neckStretchL` |
| 牙齿 | `CTRL_expressions_teethFwdU`, `CTRL_expressions_teethDownD` |

## 蓝图用法

> **注意**：`MetaHumanControlsConversionTest` 是纯测试模块，无公开蓝图 API。以下信息基于插件整体架构推断。

MetaHuman Animator 的核心功能主要通过 **编辑器工具面板**（而非蓝图节点）使用。主要工作流在 MetaHuman Toolkit 编辑器面板中完成。

主要工作流入口：

| 功能 | 说明 | 所在模块 |
|---|---|---|
| 创建 MetaHuman Identity | 从捕捉数据创建面部身份 | `MetaHumanIdentity` |
| 导入捕捉素材 | 加载和预处理面部捕捉视频 | `MetaHumanFootageIngest` |
| 运行面部拟合 | 将 MetaHuman 网格拟合到捕捉数据 | `MetaHumanFaceFittingSolver` |
| 求解面部动画 | 将捕捉数据转换为动画控制 | `MetaHumanFaceAnimationSolver` |
| 批量处理 | 对多个素材执行统一处理流程 | `MetaHumanBatchProcessor` |

## C++ 用法

### 控制参数转换验证

来自 `MetaHumanControlsConversionTest` 模块，展示如何验证面部控制参数转换的正确性。

**头文件引入**

```cpp
#include "MetaHumanControlsConversionTestModule.h"
```

**从 DNA 文件提取控制映射**（来自 `Source/MetaHumanControlsConversionTest/Private/Tests/ConversionDataGenerator.h`）

```cpp
#include "ConversionDataGenerator.h"

// 从 DNA 文件读取控制参数映射关系并写入文件
// DNA 是 MetaHuman 的专有面部数据格式
void ExportMappings(const FString& InDnaFilePath)
{
    WriteMappingsInfoFromDnaToFile(InDnaFilePath);
}
```

**测试数据结构说明**（来自 `Source/MetaHumanControlsConversionTest/Private/Tests/ControlsTestData.h`）

```cpp
// Solve Controls → Rig Controls 的转换验证数据
// InputSolveControls: 求解器输出的面部控制参数（带轴向后缀）
// ExpectedRigControls: 期望转换后的 Rig 控制参数（无轴向后缀）

// 示例：如何读取测试数据验证转换结果
#include "Tests/ControlsTestData.h"

void VerifyConversion()
{
    // 遍历求解器输出
    for (const auto& [ControlName, Value] : SolveControlsTestData::InputSolveControls)
    {
        // ControlName = "CTRL_L_brow_down.ty"
        // Value = 0.196608633f
        
        // 转换后的 Rig 控制应映射到对应的名称
        // 例如: "CTRL_L_brow_down.ty" → "CTRL_expressions_browDownL"
    }
    
    // 边界值测试：MinControlsTestData 中所有输入均为 -1.0
    // 用于验证极端输入下的转换行为
    for (const auto& [ControlName, Value] : MinControlsTestData::InputSolveControls)
    {
        // Value 始终为 -1.0
        // 验证转换函数在极值输入下的鲁棒性
    }
}
```

### 控制参数分类概览

从测试数据中可提取完整的面部控制参数体系（共约 85 个 Solve Controls → 约 200+ Rig Controls）：

| Solve 控制类别 | 参数数量 | 轴向 | Rig 对应 |
|---|---|---|---|
| 眉毛（brow） | 8 | .ty | `CTRL_expressions_brow*L/R` |
| 眼睛（eye） | 8 | .ty, .tx | `CTRL_expressions_eye*L/R` |
| 鼻子（nose） | 6 | .ty, .tx | `CTRL_expressions_nose*L/R` |
| 嘴部（mouth） | ~40 | .ty | `CTRL_expressions_mouth*L/R` |
| 下巴（jaw） | 4 | .ty, .tx | `CTRL_expressions_jaw*` |
| 舌头（tongue） | 8 | .ty, .tx | `CTRL_expressions_tongue*` |

## Demo 示例

`MetaHumanControlsConversionTest` 是自动化测试模块，不提供运行时 Demo。以下是最小化运行测试的示例：

### MetaHumanControlsConversionTestModule.h

```cpp
// Source/MetaHumanControlsConversionTest/Private/MetaHumanControlsConversionTestModule.h

#pragma once

#include "Modules/ModuleManager.h"

class FMetaHumanControlsConversionTestModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### MetaHumanControlsConversionTestModule.cpp

```cpp
// Source/MetaHumanControlsConversionTest/Private/MetaHumanControlsConversionTestModule.cpp

#include "MetaHumanControlsConversionTestModule.h"

#define LOCTEXT_NAMESPACE "FMetaHumanControlsConversionTestModule"

void FMetaHumanControlsConversionTestModule::StartupModule()
{
    // 测试模块启动时注册自动化测试
}

void FMetaHumanControlsConversionTestModule::ShutdownModule()
{
    // 清理资源
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMetaHumanControlsConversionTestModule, MetaHumanControlsConversionTest)
```

### 运行测试

在 UE 编辑器中通过自动化测试面板运行，或使用命令行：

```bash
# 运行 MetaHuman 控制转换相关测试
UnrealEditor-Cmd.exe ProjectName -ExecCmds="Automation RunTests MetaHuman" -Unattended -NullRHI -NoSound
```

## 模块依赖

从各模块的 Build.cs 依赖关系中提取**非标准依赖**：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库（底层面部处理算法） |
| `ControlRigDeveloper` | Control Rig 开发工具（面部 Rig 集成） |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器扩展 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体工具函数 |
| `MetaHumanImageViewerEditor` | 捕获数据图像预览 |

> 如果你的模块仅需基本的 MetaHuman 功能（如查询身份数据），依赖 `MetaHumanIdentity` 即可。若需完整的处理流水线，需额外依赖 `MetaHumanPipeline` 及相关处理模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已存在网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

- **活跃维护** ✅：近一周内有多次实质性功能更新和 Bug 修复
- **持续迭代**：从 commit 记录看，团队持续在改进身体追踪集成、序列器功能和渲染质量
- **Epic 官方支持**：作为 Epic Games 官方产品级插件，有专门团队维护
- **实验性/已知限制**：
  - 部分功能依赖外部 MetaHuman 服务和 CoreTechLib 库
  - 身体追踪（Body Tracking）相关功能仍在积极开发中
  - 需要较新的硬件（如 iPhone X 及以上用于面部捕捉）
- **推荐使用**：强烈推荐用于 MetaHuman 角色面部动画生产流程。该插件是目前 UE5 生态中最完整的面部捕捉→动画解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/)
- [测试用例 - ControlsConversionTest](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest/Private/Tests/)
- [MetaHuman Creator](https://metahuman.unrealengine.com/)