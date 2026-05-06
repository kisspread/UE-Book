# MoverCVDEditor (Mover 子模块)

> Mover 插件中用于 Chaos Visual Debugger (CVD) 的编辑器支持模块，负责显示和调试 Mover 角色的移动模拟数据。

| 属性 | 值 |
|---|---|
| 中文名 | Mover 可视化调试扩展 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MoverCVDEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/Mover/Source/MoverCVDEditor) | |

## 用途

MoverCVDEditor 是 Mover 插件的编辑器配套模块，专为 Chaos Visual Debugger（CVD）设计。它扩展了 CVD 的功能，允许开发者在可视化调试会话中查看 Mover 驱动的 Actor 内部状态（如同步状态、输入命令、本地模拟数据）。该模块主要包含：

- **`FMoverCVDExtension`** – 在 CVD 中注册自定义 Tab（`MoverCVDTab`）和数据处理器（`FMoverCVDSimDataProcessor`）。
- **`UMoverCVDSimDataComponent`** – 存储每一帧反序列化后的 Mover 模拟数据，供 CVD 显示。
- **`FMoverCVDSimDataProcessor`** – 接收游戏运行时通过 trace 发送的 Mover 模拟数据并反序列化。
- **`UMoverCVDSimDataSettings`** – 配置调试绘制的显示选项（如文字、深度优先级、线条粗细）。
- **`FMoverCVDTab`** – 一个用于展示选中粒子的 Mover 详细信息的 CVD 标签页。
- **`FMoverCVDStyle`** – 定义模块使用的 Slate 样式。

该模块解决了 Mover 开发中的两大痛点：1）缺少运行时可观察的内部状态；2）难以定位回滚网络导致的移动异常。通过 CVD 集成，开发者可以像使用游戏内置高性能工具一样，在编辑器环境下单帧查看角色移动的完整路径和决策依据。

## 使用场景

- 开发使用 Mover 作为移动方式的多人游戏（如射击、动作游戏），需要反复调试角色移动逻辑。
- 排查网络回滚不一致问题：通过 CVD 录制一局游戏，然后回放并观察 Mover 的 SyncState、InputCmd 在每个帧的变化。
- 在没有实际游戏环境的情况下，通过 CVD 加载记录文件来分析角色移动行为。
- 扩展自定义 Mover 模式时，验证新模式的模拟结果是否符合预期。

## 蓝图用法

该模块主要面向 C++ 和 CVD 工具，**不提供直接的蓝图可调用节点**。但可以通过以下方式间接使用：

1. 在游戏代码中启用 Mover 的 trace 录制（需 Mover 核心模块支持）。
2. 在 CVD 中查看时，MoverCVDTab 会自动显示选中粒子的 Mover 信息。

若有自定义需求，可在 C++ 中继承 `UMoverCVDSimDataComponent` 扩展可视化数据。

## C++ 用法

### 头文件引入

```cpp
#include "MoverCVDEditor.h"
#include "MoverCVDSimDataComponent.h"
#include "MoverCVDExtension.h"
#include "MoverCVDTab.h"
#include "MoverCVDSimDataProcessor.h"
#include "MoverCVDSimDataSettings.h"
```

### 基本用法

```cpp
// 在模块启动时，FMoverCVDEditorModule 会自动注册扩展和 Tab
// 无需手动调用

// 若需要强制重新加载所有 solver 的 mover 数据组件（例如场景切换时）：
void UMyCVDHelper::RefreshMoverData()
{
    // 通过 CVD 场景获取所有 Mover 数据组件
    TSharedPtr<FChaosVDScene> Scene = /* 从 Tab 或 CVD 实例获取 */;
    if (Scene)
    {
        FMoverCVDTab* MoverTab = /* 获取当前激活的 MoverCVDTab */;
        if (MoverTab)
        {
            // 触发内部重新检索 SolverToSimDataComponentMap
            // MoverTab 会调用 RetrieveAllSolversMoverDataComponents()
        }
    }
}
```

来源：`Source/MoverCVDEditor/Private/MoverCVDTab.h` 中 `RetrieveAllSolversMoverDataComponents` 方法的注释。

### 进阶用法

#### 自定义数据展示

若需要为 Mover 模式添加额外的可视化字段，可以继承 `UMoverCVDSimDataComponent` 并重写 `UpdateFromSolverFrameData`：

```cpp
UCLASS()
class UMyMoverSimDataComponent : public UMoverCVDSimDataComponent
{
    GENERATED_BODY()
public:
    virtual void UpdateFromSolverFrameData(const FChaosVDSolverFrameData& InSolverFrameData) override
    {
        Super::UpdateFromSolverFrameData(InSolverFrameData);
        // 自定义反序列化或额外数据提取
        // 注：当前实现将数据附加到 FChaosVDTraceProvider::GetCurrentSolverFrame()
    }
};
```

#### 启用调试绘制

```cpp
// 在设置中启用可视化标志
UMoverCVDSimDataSettings::SetDataVisualizationFlags(EMoverCVDSimDataVisualizationFlags::EnableDraw);
// 控制是否显示文字、线条粗细等
if (UMoverCVDSimDataSettings* Settings = GetMutableDefault<UMoverCVDSimDataSettings>())
{
    Settings->bShowDebugText = true;
    Settings->BaseThickness = 3.0f;
    Settings->DepthPriority = SDPG_Foreground;
}
```

来源：`Source/MoverCVDEditor/Private/MoverCVDSimDataSettings.h`

## Demo 示例

以下示例演示如何在 CVD 插件的自定义 tab 中使用 `UMoverCVDSimDataComponent` 来获取选中粒子的 Mover 信息（来自 `FMoverCVDTab::DisplaySingleParticleInfo` 简化版）：

**MoverCVDHelper.h**
```cpp
#pragma once

#include "MoverCVDTab.h"

class FMoverCVDHelper
{
public:
    static void ShowMoverInfoForParticle(TSharedPtr<FMoverCVDTab> MoverTab, int32 SolverID, int32 ParticleID)
    {
        // 通常 MoverCVDTab 会在 HandlePostSelectionChange 中自动调用此逻辑
        // 此处仅为演示手动触发
        UMoverCVDSimDataComponent* DataComp = /* 从 Scene 获取 */;
        if (!DataComp) return;

        TSharedPtr<FMoverCVDSimDataWrapper> Wrapper;
        TSharedPtr<FMoverSyncState> SyncState;
        TSharedPtr<FMoverInputCmdContext> InputCmd;
        TSharedPtr<FMoverDataCollection> LocalSimData;
        if (DataComp->FindAndUnwrapSimDataForParticle(ParticleID, Wrapper, SyncState, InputCmd, LocalSimData))
        {
            // 现在可以访问 SyncState, InputCmd, LocalSimData 用于显示
            UE_LOG(LogTemp, Log, TEXT("Particle %d Mover SyncState: %s"), ParticleID, *SyncState->ToDebugString());
        }
    }
};
```

## 模块依赖

从 `MoverCVDEditor.Build.cs`（位于 `Engine/Plugins/Experimental/Mover/Source/MoverCVDEditor/`）可知，该模块需要以下独特依赖（省略标准依赖）：

| 模块 | 用途 |
|---|---|
| `ChaosVD` | 核心 CVD 框架，包括 `FChaosVDExtension`、`SChaosVDMainTab`、`FChaosVDScene`、数据选择机制等 |
| `Mover` | Mover 核心模块，提供 `FMoverSyncState`、`FMoverInputCmdContext`、`FMoverDataCollection` 等数据结构 |
| `MoverCVDData` | 运行时 trace 数据定义，如 `FMoverCVDSimDataWrapper` |
| `ChaosVDRuntime` | CVD 运行时组件，如 `UChaosVDSolverDataComponent` |
| `SlateCore` | Slate UI 核心，用于 `SDockTab` 等 |
| `ToolWidgets` | 工具小组件（如 `SChaosVDDetailsView`） |
| `TedsCore`、`TedsUtils` | 结构化元素数据系统，用于 `ChaosVDStructTypedElementData` |

## 维护状态

### 近期更新

- 2025-11-18 [c94b0582] Mover: fix issue where montages with a non-zero start time would be played from the wrong position o
- 2025-11-18 [0b7174b5] Mover: Fixing debug editor crash when initializing a CircularBuffer with a capacity of 0 on MoverCom
- 2025-11-18 [796d840a] Mover: Fixing debug editor crash when initializing a CircularBuffer with a capacity of 0 on MoverCom
- 2025-11-18 [0c5c955f] Mover: Adding virtual destructor to BlackboardEntryBase struct to fix a memory leak.

### 维护评价

该模块自创建（2025-11-18）以来，在同一日即有多次功能性修复和质量改进提交，表明开发团队对 Mover 及相关工具模块非常重视。修复内容涉及编辑器崩溃、内存泄漏和动画播放问题，显示出积极维护状态。由于创建时间极短，目前处于快速迭代期，推荐在有 Mover 使用需求的开发中启用。

**警告**：该模块属于实验性功能，API 可能在未来版本中发生较大变动，建议在正式项目中使用时做好版本锁定和回归测试。

## 相关链接

- [源码 (MoverCVDEditor 模块)](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/Mover/Source/MoverCVDEditor/)
- [官方文档 (Mover 插件)](https://docs.unrealengine.com/5.7/API/Plugins/Mover/) （未提供具体链接，请参考 UE 官方文档）
- [测试用例 (Mover 整体)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mover/Tests) （可能存在，但未列出）