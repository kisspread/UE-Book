# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画器 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（动画资产、配置文件、核心算法库） |
| 模块 | `MetaHumanConfigEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 为 Unreal Engine 开发的官方 MetaHuman 动画制作工具套件。它解决的核心问题是**从面部捕捉数据（如 iPhone 深度摄像头、专业动捕设备等）驱动高保真 MetaHuman 数字人角色进行逼真面部动画**。

该插件提供了一整套完整的流水线，包括：
- **面部追踪与轮廓检测**：从视频或深度序列中提取关键的面部特征点和轮廓。
- **动画求解**：将捕捉的表演数据转换为 MetaHuman 骨骼可用的动画控制。
- **面部拟合**：确保捕捉的数据能够精确地适配到特定的 MetaHuman 模型上。
- **性能优化**：提供用于实时或近实时动画驱动的解决方案。
- **集成与批处理**：支持与 Sequencer 集成进行时间线编辑，并提供批处理能力。

它的存在是为了让影视、游戏、虚拟主播等领域的创作者，能够高效、精确地将真实演员的面部表演“转移”到虚拟的 MetaHuman 角色上，实现令人信服的数字人表演。

## 使用场景

- 你正在为电影或电视节目制作高质量的数字人过场动画，并需要将演员的现场表演录制下来 → 使用 MetaHuman Animator 的**面部捕捉数据导入、追踪与求解**功能。
- 你是一个虚拟主播（VTuber），希望自己的 MetaHuman 虚拟形象能够实时模仿你的面部表情 → 使用 MetaHuman Animator 的**实时性能驱动**模块。
- 你需要为游戏中的 NPC 批量生成大量基于真人表演的口型同步和表情动画 → 使用 MetaHuman Animator 的**批处理**功能。
- 你已经通过 iPhone 的 LiDAR 或其它方式录制了面部表演数据，需要将其应用到 UE 中的 MetaHuman 角色上 → 使用完整的**数据处理流水线**。

## 蓝图用法

MetaHuman Animator 的蓝图节点主要集中在 `MetaHumanConfigEditor` 模块以及后续可能出现的 `MetaHumanPerformance`、`MetaHumanIdentity` 等模块中。`MetaHumanConfigEditor` 本身主要提供编辑器内的配置界面支持。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SMetaHumanConfigCombo::Construct` | （内部 Slate 控件）构建用于选择 MetaHuman 配置类型的下拉框。 | `SMetaHumanConfigCombo` |
| `UMetaHumanConfigFactory::FactoryCreateFile` | （编辑器功能）将外部的配置文件（如 `.mha` 文件）导入并创建为 `UMetaHumanConfig` 资产。 | `UMetaHumanConfigFactory` |

**说明**：由于 MetaHuman Animator 的核心功能（如动画求解、追踪）通常是通过专用编辑器工具窗口（如 MetaHuman Animator 面板）或数据资产触发的，其暴露给普通蓝图的通用 `BlueprintCallable` 函数相对有限。更复杂的动画控制和数据流通常在 C++ 层面或通过 `ControlRig` 等系统完成。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanConfigEditor.h"
#include "MetaHumanConfig.h" // 假设的基础配置类
```

### 基本用法

**创建和管理 MetaHuman 配置**

```cpp
// 假设你想通过代码创建一个新的 MetaHuman 配置资产
// （这通常由编辑器工厂 UMetaHumanConfigFactory 处理，但这是底层逻辑示例）
UPackage* Package = CreatePackage(*FString::Printf(TEXT("/Game/MyMetaHumans/%s"), *ConfigName));
UMetaHumanConfig* NewConfig = NewObject<UMetaHumanConfig>(Package, *ConfigName, RF_Public | RF_Standalone);
NewConfig->MarkPackageDirty();
```

**使用资产定义 (Asset Definition)**

```cpp
// 通过资产定义获取 MetaHuman 配置资产的显示信息
// (通常在编辑器上下文中使用，例如用于资产浏览器或右键菜单)
UAssetDefinition_MetaHumanConfig* AssetDef = GetDefault<UAssetDefinition_MetaHumanConfig>();
FText DisplayName = AssetDef->GetAssetDisplayName(); // 例如 “MetaHuman Config”
FLinearColor Color = AssetDef->GetAssetColor(); // 资产在编辑器中显示的颜色
```

### 进阶用法

结合 `MetaHumanConfigEditor` 和其他模块（如 `MetaHumanIdentity`, `MetaHumanPerformance`），你可以构建自定义的动画处理流程。

```cpp
// 伪代码：描述一个可能的自动化处理流程
// 1. 加载一个 MetaHuman 身份资产 (Identity)
UMetaHumanIdentity* Identity = LoadObject<UMetaHumanIdentity>(nullptr, TEXT("/Game/MH/Identity_MyCharacter"));

// 2. 使用该身份关联一个配置 (Config)
UMetaHumanConfig* Config = GetConfigForIdentity(Identity); // 假设的函数

// 3. 将捕捉数据输入到管道 (Pipeline) 中进行处理
// MetaHumanPipeline, MetaHumanFaceAnimationSolver 等模块会在此介入
// 4. 最终生成动画序列并应用到 Skeletal Mesh Component
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何在一个编辑器工具中展示 MetaHuman 配置资产的选择界面。

```cpp
// MyMetaHumanTool.h
#pragma once
#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "MetaHumanConfig.h"

class SMyMetaHumanTool : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyMetaHumanTool) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<class SMetaHumanConfigCombo> ConfigSelector;
};
```

```cpp
// MyMetaHumanTool.cpp
#include "MyMetaHumanTool.h"
#include "SMetaHumanConfigCombo.h"
#include "PropertyHandle.h"

void SMyMetaHumanTool::Construct(const FArguments& InArgs)
{
    // 创建一个 MetaHuman 配置类型选择器
    // EMetaHumanConfigType 是一个枚举，定义了配置的用途（如面部动画、音频驱动等）
    // 这里我们传入一个虚拟的属性句柄，实际使用中可能需要关联到真正的资产属性
    TSharedPtr<IPropertyHandle> DummyPropertyHandle; // 需要从实际资产获取

    ChildSlot
    [
        SNew(SMetaHumanConfigCombo)
        // 注意：SMetaHumanConfigCombo 的 Construct 函数需要额外参数，这里为演示简化了调用
    ];
}
```

## 模块依赖

**使用此插件（或其子模块）的特殊依赖**：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心算法库，包含面部追踪、求解等核心计算逻辑。 |
| `SkeletalMeshUtilitiesCommon` | 用于操作骨骼网格体的通用工具。 |
| `ControlRigDeveloper` | 与 ControlRig 系统集成，用于驱动最终的动画。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分。 |

*省略了所有常见的基础依赖（Core, Engine, Slate 等）。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出功能，避免冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 进行身体追踪时过滤掉不必要的可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 支持为已存在的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复与 Sequencer 集成时的缓存问题。 |

### 维护评价

MetaHuman Animator 是 Epic Games 为 MetaHuman 生态推出的官方、核心工具插件，**维护极其活跃**。
- **创建时间**：虽然具体日期未知，但作为5.0版本后推出的新系统，年龄很短（🆕）。
- **更新频率**：从提交历史看，近期（2026年5月）有多次连续的功能更新和Bug修复，开发非常密集。
- **活跃度**：毫无疑问，该插件是 Epic 重点投入和维护的项目，处于**积极开发**阶段。
- **已知问题**：作为复杂的新系统，可能存在特定配置或边缘情况下的Bug（如提交记录中的渲染瑕疵修复），但都在快速解决中。
- **推荐使用**：**强烈推荐**。对于任何需要创建高保真数字人动画的 UE5 项目，这是官方且功能最完整的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 官方文档：暂无直接链接，请参考 Epic Games 官方文档和学习平台。
- 测试用例：可能位于 `Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests` 或 `Engine/Tests` 下的对应目录。