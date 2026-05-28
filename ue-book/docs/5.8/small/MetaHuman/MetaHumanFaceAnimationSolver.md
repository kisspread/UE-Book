# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画配置资产、求解器模板、UI 样式） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MeshTrackerInterface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-06-01（估算） |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的 MetaHuman 动画制作工具链，用于从面部捕捉数据生成高保真的 MetaHuman 面部动画。它不是一个简单的"一键生成"工具，而是一个完整的管线（Pipeline），涵盖以下核心环节：

1. **面部追踪（Face Contour Tracking）**：从视频素材中检测和追踪面部特征点，提取深度信息
2. **面部拟合求解（Face Fitting Solver）**：将追踪数据映射到 MetaHuman 面部网格上
3. **面部动画求解（Face Animation Solver）**：将追踪结果转换为面部骨骼控制器动画，支持深度图影响、牙齿追踪模式、眼部平滑等参数调节
4. **身份构建（Identity）**：从照片或视频中创建 MetaHuman 身份资产
5. **表演捕捉（Performance）**：从单次表演中提取动画数据
6. **语音驱动面部（Speech2Face）**：从音频生成面部动画
7. **批量处理（Batch Processor）**：自动化处理大量捕捉数据

**为什么存在**：MetaHuman Creator 生成的数字人需要动画才能"活起来"。传统面部动画需要昂贵的专业设备和复杂的后期流程，MetaHuman Animator 旨在用软件算法替代这一过程，支持从 iPhone 深度相机到专业头戴摄像机等多种输入设备。

## 使用场景

- 你有一个 MetaHuman 角色，需要从 iPhone 录制的深度视频生成面部动画 → 使用 MetaHuman Animator 的捕捉数据导入 + 面部动画求解流程
- 你有一段对话表演视频，需要提取出唇形同步动画 → 使用 MetaHumanPerformance + MetaHumanFaceAnimationSolver
- 你只有音频文件，想快速生成面部口型动画 → 使用 MetaHumanSpeech2Face
- 你需要批量处理 100 段表演数据 → 使用 MetaHumanBatchProcessor
- 你要从多角度照片创建一个新 MetaHuman 角色 → 使用 MetaHumanIdentity

## 蓝图用法

MetaHuman Animator 主要面向编辑器工作流，大部分操作在专用面板中完成。运行时可用的 BlueprintCallable API 集中在求解器配置和数据查询上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CanProcess` | 检查求解器当前配置是否可用于处理 | `UMetaHumanFaceAnimationSolver` |
| `SettingsOverridden` | 检查是否有参数被用户手动覆盖（而非使用默认值） | `UMetaHumanFaceAnimationSolver` |
| `GetConfigDisplayName` | 获取当前有效配置的显示名称 | `UMetaHumanFaceAnimationSolver` |
| `GetSolverTemplateData` | 获取求解器模板数据的 JSON 字符串 | `UMetaHumanFaceAnimationSolver` |
| `GetSolverConfigData` | 获取求解器配置数据的 JSON 字符串 | `UMetaHumanFaceAnimationSolver` |
| `GetSolverDefinitionsData` | 获取求解器定义数据的 JSON 字符串 | `UMetaHumanFaceAnimationSolver` |
| `GetSolverHierarchicalDefinitionsData` | 获取层级定义数据（用于层级骨骼求解） | `UMetaHumanFaceAnimationSolver` |
| `SetEasyToEditControlConstraints` | 设置易于编辑的控制约束（静态方法） | `UMetaHumanFaceAnimationSolver` |

### 使用示例（蓝图描述）

**配置动画求解参数：**

1. 创建一个 `MetaHumanFaceAnimationSolver` 资产
2. 在 Details 面板中勾选 `bOverrideDepthMapInfluence`，将其设为 `High`（充分利用深度图信息）
3. 勾选 `bOverrideEyeSolveSmoothness`，将滑块设为 `0.3`（适度平滑眼部运动）
4. 勾选 `bOverrideTeethMode`，选择 `Estimated`（使用估算模式，适用于没有牙齿追踪点的场景）

**检查求解器就绪状态：**

```
[FaceAnimationSolver] → [CanProcess] → [Branch]
                                           ├─ True  → 开始处理
                                           └─ False → 提示配置不完整
```

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceAnimationSolver.h"
```

### 基本用法

```cpp
// 创建面部动画求解器实例并配置参数
// 来源: Source/MetaHumanFaceAnimationSolver/Public/MetaHumanFaceAnimationSolver.h

UMetaHumanFaceAnimationSolver* Solver = NewObject<UMetaHumanFaceAnimationSolver>();

// 启用深度图影响覆盖
Solver->bOverrideDepthMapInfluence = true;
Solver->DepthMapInfluence = EDepthMapInfluenceValue::High;

// 启用眼部平滑覆盖
Solver->bOverrideEyeSolveSmoothness = true;
Solver->EyeSolveSmoothness = 0.2f;  // 范围 0.0 ~ 1.0

// 启用牙齿模式覆盖
Solver->bOverrideTeethMode = true;
Solver->TeethMode = ETeethMode::Estimated;

// 检查是否可以处理
if (Solver->CanProcess())
{
    // 获取求解器配置数据（JSON 字符串格式）
    FString ConfigData = Solver->GetSolverConfigData();
    FString TemplateData = Solver->GetSolverTemplateData();
    FString DefinitionsData = Solver->GetSolverDefinitionsData();

    UE_LOG(LogTemp, Log, TEXT("Solver ready, config: %s"), *ConfigData);
}
```

### 进阶用法

```cpp
// 使用设备配置覆盖 + 监听内部变化
// 来源: Source/MetaHumanFaceAnimationSolver/Public/MetaHumanFaceAnimationSolver.h

UMetaHumanFaceAnimationSolver* Solver = NewObject<UMetaHumanFaceAnimationSolver>();

// 覆盖设备配置（例如指定 iPhone 深度相机的配置）
Solver->bOverrideDeviceConfig = true;
Solver->DeviceConfig = MyCustomMetaHumanConfig;  // UMetaHumanConfig* 资产

// 绑定变化回调（用于编辑器 UI 响应参数修改）
FDelegateHandle Handle = Solver->OnInternalsChanged().AddLambda([Solver]()
{
    // 当求解器内部参数发生变化时，重新获取配置数据
    FString DisplayName;
    if (Solver->GetConfigDisplayName(nullptr, DisplayName))
    {
        UE_LOG(LogTemp, Log, TEXT("Config changed: %s"), *DisplayName);
    }
});

// 获取层级定义数据（适用于层级骨骼动画求解）
FString HierarchicalData = Solver->GetSolverHierarchicalDefinitionsData();
FString HierarchicalPlusChinData = Solver->GetSolverHierarchicalDefinitionsPlusChinCompressData();

// 获取 PCA 从 DNA 的转换数据
FString PCAFromDNAData = Solver->GetSolverPCAFromDNAData();

// 将配置数据设置为易于编辑的约束模式
FString ModifiedConfig = UMetaHumanFaceAnimationSolver::SetEasyToEditControlConstraints(ConfigData);

// 清理委托
Solver->OnInternalsChanged().Remove(Handle);
```

## 枚举类型参考

| 枚举 | 值 | 说明 |
|---|---|---|
| `EDepthMapInfluenceValue` | `None` | 不使用深度图 |
| | `Low` | 低影响，深度图作为轻微参考 |
| | `High` | 高影响，深度图显著影响求解结果 |
| `ETeethMode` | `TrackingPoints` | 使用追踪点数据驱动牙齿动画（精度高，需要追踪点） |
| | `Estimated` | 估算牙齿位置（适用范围广，精度较低） |

## Demo 示例

```cpp
// MetaHumanFaceAnimationSolverExample.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "MetaHumanFaceAnimationSolverExample.generated.h"

class UMetaHumanFaceAnimationSolver;

UCLASS()
class UMetaHumanFaceAnimationSolverExample : public UEngineSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    /** 创建并配置一个求解器 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|Example")
    UMetaHumanFaceAnimationSolver* CreateConfiguredSolver();

    /** 获取求解器的完整配置信息 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|Example")
    bool GetSolverConfiguration(
        UMetaHumanFaceAnimationSolver* Solver,
        FString& OutConfigJSON,
        FString& OutTemplateJSON
    );
};
```

```cpp
// MetaHumanFaceAnimationSolverExample.cpp
#include "MetaHumanFaceAnimationSolverExample.h"
#include "MetaHumanFaceAnimationSolver.h"

void UMetaHumanFaceAnimationSolverExample::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    UE_LOG(LogTemp, Log, TEXT("MetaHuman Face Animation Solver Example initialized"));
}

UMetaHumanFaceAnimationSolver* UMetaHumanFaceAnimationSolverExample::CreateConfiguredSolver()
{
    UMetaHumanFaceAnimationSolver* Solver = NewObject<UMetaHumanFaceAnimationSolver>();
    if (!Solver)
    {
        return nullptr;
    }

    // 配置为高质量面部动画模式
    Solver->bOverrideDepthMapInfluence = true;
    Solver->DepthMapInfluence = EDepthMapInfluenceValue::High;

    Solver->bOverrideEyeSolveSmoothness = true;
    Solver->EyeSolveSmoothness = 0.15f;

    Solver->bOverrideTeethMode = true;
    Solver->TeethMode = ETeethMode::TrackingPoints;

    return Solver;
}

bool UMetaHumanFaceAnimationSolverExample::GetSolverConfiguration(
    UMetaHumanFaceAnimationSolver* Solver,
    FString& OutConfigJSON,
    FString& OutTemplateJSON)
{
    if (!Solver || !Solver->CanProcess())
    {
        return false;
    }

    OutConfigJSON = Solver->GetSolverConfigData();
    OutTemplateJSON = Solver->GetSolverTemplateData();
    return true;
}
```

## 模块依赖

MetaHumanAnimator 包含 27 个模块，相互之间有紧密的依赖关系。以下是使用 **MetaHumanFaceAnimationSolver** 模块时需要关注的独特依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanConfig` | 提供 UMetaHumanConfig 配置资产类型，求解器通过它获取设备特定参数 |
| `MetaHumanCoreTechLib` | MetaHuman 核心计算库（MetaHumanConfig 的依赖） |
| `MetaHumanCore` | 提供 MetaHuman 核心类型和基础设施 |
| `MetaHumanPipeline` | 处理管线框架，将追踪、拟合、求解串联为完整工作流 |
| `MetaHumanIdentity` | MetaHuman 身份资产系统，管理角色身份和面部网格 |
| `MetaHumanCaptureDataEditor` | 捕捉数据的编辑器支持，求解器通过它获取 UCaptureData |
| `MetaHumanCaptureProtocolStack` | 捕捉协议栈，处理设备通信 |
| `MetaHumanDepthGenerator` | 深度图生成，为求解器的 DepthMapInfluence 参数提供深度数据 |
| `MetaHumanFaceContourTracker` | 面部轮廓追踪器，为求解器提供追踪点输入 |
| `MetaHumanFaceFittingSolver` | 面部拟合求解器，与动画求解器配合完成完整管线 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器支持（MetaHumanIdentity 的依赖） |
| `ControlRigDeveloper` | ControlRig 开发支持，用于面部骨骼控制器输出 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

MetaHuman Animator 是 **活跃维护** 的旗舰插件：

- **创建时间**：约 2023 年，随着 MetaHuman Animator 产品发布引入 UE5
- **更新频率**：非常活跃，最近一次更新仅在 2 天前（2026-05-22），且每周有多次提交
- **更新质量**：持续的功能增强（身体追踪集成、动画序列导出）和 Bug 修复（渲染瑕疵、Sequencer 缓存）
- **源码规模**：544 个源文件，27 个模块，属于大型工程级插件
- **平台支持**：Win64、Linux、Mac 三平台

**⚠️ 注意事项**：
- 此插件 `EnabledByDefault=false`（`"Installed": false`），需要在插件管理器中手动启用
- 依赖 MetaHuman CoreTech Lib 等专有库，部分功能可能需要 Epic Games 的额外许可
- 完整功能链（从捕捉到动画输出）涉及多个模块的协作，单独使用某个模块可能受限

**推荐使用**：✅ 如果你在使用 MetaHuman 角色制作面部动画，这是官方的、目前唯一的集成解决方案，强烈推荐。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/meta-human-animator-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)