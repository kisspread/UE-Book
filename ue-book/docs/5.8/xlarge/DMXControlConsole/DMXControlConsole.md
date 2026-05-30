# DMX Control Console

> Console that can be patched from DMX Libraries and sends DMX to Output Ports

| 属性 | 值 |
|---|---|
| 中文名 | DMX 控制台 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXControlConsole` (Runtime), `DMXControlConsoleEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-17 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXControlConsole) | |

## 用途

DMX Control Console 是一个**虚拟 DMX 控制台**，允许用户在 Unreal Engine 中通过 GUI 控制台界面直接控制 DMX 灯具。它解决的核心问题是：在虚拟制片（Virtual Production）场景下，用户需要一种**可视化、交互式**的方式来实时控制 DMX 灯光设备。

该插件的工作流程为：

1. **从 DMX Library 导入灯具配置**：自动根据 DMX Library 中的 Fixture Patch 生成对应的 Fader 组
2. **通过 Fader 控制 DMX 值**：每个 Fader 对应一个或多个 DMX 通道，支持不同数据格式（8/16/24 位）
3. **发送 DMX 数据到 Output Port**：将控制台的状态实时发送到物理 DMX 设备
4. **Cue 记忆系统**：保存和回放 Fader 状态快照
5. **Oscillator 系统**：提供正弦波和方波振荡器，用于自动生成变化的 DMX 信号（如灯光明暗呼吸效果）

与直接在蓝图中使用 DMX Protocol 插件发送数据相比，本插件提供了更接近**真实灯光控制台**的操作体验，适合需要频繁调整灯光参数的场景。

## 使用场景

- 你在做虚拟制片项目，需要在编辑器中实时调整 DMX 灯具亮度/颜色 → 用 DMX Control Console Actor
- 你已经配置好 DMX Library 和 Fixture Patch，想要一个可视化的控制面板来调试 → 从 DMX Library 自动生成 Fader 组
- 你需要保存多组灯光状态并在演出中快速切换 → 使用 Cue Stack
- 你需要灯光明暗呼吸、闪烁等自动效果 → 使用内置 Oscillator（Sine Wave / Square Wave）
- 你需要在编辑器中预览 DMX 输出效果（不运行游戏） → 启用 Actor 的 "Send DMX in Editor"

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Sending DMX` | 开始发送 DMX 数据 | `ADMXControlConsoleActor` |
| `Stop Sending DMX` | 停止发送 DMX 数据 | `ADMXControlConsoleActor` |
| `Pause Sending DMX` | 暂停 DMX 发送（保持最后状态） | `ADMXControlConsoleActor` |
| `Reset To Default` | 将所有 Fader 重置为默认值 | `ADMXControlConsoleActor` |
| `Reset To Zero` | 将所有 Fader 重置为零 | `ADMXControlConsoleActor` |
| `Get Control Console Data` | 获取控制台数据对象 | `ADMXControlConsoleActor` |

### Oscillator 蓝图属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `Frequency Hz` | float | 波形频率（Hz） | `UDMXControlConsoleFloatOscillator_Sine` / `_Square` |
| `Amplitude` | float | 波形振幅 [0, 1] | 同上 |
| `Offset` | float | 波形偏移 [0, 1] | 同上 |
| `Get Normalized Value` | BlueprintNativeEvent | 获取归一化值（供蓝图重写） | `UDMXControlConsoleFloatOscillator` |

### 使用示例（蓝图描述）

**基本使用流程**：

1. 在场景中放置 `DMXControlConsoleActor`
2. 选中该 Actor，在 Details 面板中设置 `DMX Library`（来自 `ControlConsoleData`）
3. 启用 `Auto Activate`（运行时自动开始发送 DMX）
4. 在蓝图中：
   - **BeginPlay** → 获取 `DMXControlConsoleActor` 引用
   - 调用 `Start Sending DMX` 开始发送
   - 需要停止时调用 `Stop Sending DMX` 或 `Pause Sending DMX`
   - 需要重置时调用 `Reset To Default` 或 `Reset To Zero`

**在编辑器中预览**：

1. 将 `ADMXControlConsoleActor` 放到关卡中
2. 勾选 `Send DMX in Editor`
3. 在控制台面板中拖动 Fader 即可实时看到 DMX 输出效果

## C++ 用法

### 头文件引入

```cpp
#include "DMXControlConsoleActor.h"
#include "DMXControlConsoleData.h"
#include "DMXControlConsoleFaderGroup.h"
#include "DMXControlConsoleFaderBase.h"
#include "DMXControlConsoleCueStack.h"
```

### 基本用法

通过 `ADMXControlConsoleActor` 控制 DMX 发送（与蓝图 API 对应）：

```cpp
// 获取场景中的 DMX Control Console Actor
ADMXControlConsoleActor* ConsoleActor = /* 通过某种方式获取引用 */;

// 开始/停止/暂停 DMX 发送
ConsoleActor->StartSendingDMX();
ConsoleActor->PauseSendingDMX();
ConsoleActor->StopSendingDMX();

// 重置所有 Fader
ConsoleActor->ResetToDefault();
ConsoleActor->ResetToZero();
```

### 进阶用法

**访问控制台数据和 Fader 组**：

```cpp
// 获取 Control Console Data
UDMXControlConsoleData* ConsoleData = ConsoleActor->GetControlConsoleData();
if (ConsoleData)
{
    // 从 DMX Library 自动生成 Fader Groups
    ConsoleData->GenerateFromDMXLibrary();

    // 获取所有 Fader Group
    TArray<UDMXControlConsoleFaderGroup*> AllGroups = ConsoleData->GetAllFaderGroups();
    
    // 遍历并操作 Fader
    for (UDMXControlConsoleFaderGroup* Group : AllGroups)
    {
        // 按 Fixture Patch 查找
        UDMXControlConsoleFaderGroup* FoundGroup = ConsoleData->FindFaderGroupByFixturePatch(MyFixturePatch);
    }
}
```

**操作单个 Fader**：

```cpp
// 遍历 Fader Group 中的所有 Fader
UDMXControlConsoleFaderGroup* FaderGroup = /* 获取引用 */;
TArray<UDMXControlConsoleFaderBase*> AllFaders = FaderGroup->GetAllFaders();

for (UDMXControlConsoleFaderBase* Fader : AllFaders)
{
    // 设置 Fader 值（根据 DataType 自动映射到 DMX 通道）
    Fader->SetValue(128);
    
    // 获取 Fader 信息
    int32 UniverseID = Fader->GetUniverseID();
    int32 StartAddr = Fader->GetStartingAddress();
    EDMXFixtureSignalFormat DataType = Fader->GetDataType();
    
    // 启用/禁用 Fader
    Fader->SetEnabled(true);
    
    // 锁定 Fader（防止值被修改）
    Fader->SetLocked(true);
}
```

**使用 Cue Stack**：

```cpp
UDMXControlConsoleData* ConsoleData = ConsoleActor->GetControlConsoleData();
UDMXControlConsoleCueStack* CueStack = ConsoleData->GetCueStack();

if (CueStack)
{
    // 保存当前 Fader 状态为一个 Cue
    TArray<UDMXControlConsoleFaderBase*> CurrentFaders = ConsoleData->GetAllFaderGroups()
        [0]->GetAllFaders();
    FDMXControlConsoleCue* NewCue = CueStack->AddNewCue(CurrentFaders, TEXT("Scene 1"), FLinearColor::Green);

    // 回放 Cue
    if (NewCue)
    {
        CueStack->Recall(*NewCue);
    }

    // 监听 Cue Stack 变化
    CueStack->GetOnCueStackChanged().AddLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("Cue Stack changed"));
    });
}
```

**监听 Fader Group 事件**：

```cpp
// 监听 Fader Group 添加/移除
ConsoleData->GetOnFaderGroupAdded().AddLambda(
    [](const UDMXControlConsoleFaderGroup* FaderGroup)
    {
        UE_LOG(LogTemp, Log, TEXT("Fader Group added: %s"), *FaderGroup->GetFaderGroupName());
    });

ConsoleData->GetOnFaderGroupRemoved().AddLambda(
    [](const UDMXControlConsoleFaderGroup* FaderGroup)
    {
        UE_LOG(LogTemp, Log, TEXT("Fader Group removed: %s"), *FaderGroup->GetFaderGroupName());
    });
```

## Demo 示例

一个最小示例：创建一个自定义 Actor，在场景中自动生成 DMX 控制台并开始发送。

**MyDMXController.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDMXController.generated.h"

class ADMXControlConsoleActor;
class UDMXControlConsoleData;

UCLASS()
class AMyDMXController : public AActor
{
    GENERATED_BODY()

public:
    AMyDMXController();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 关联的 DMX Control Console Actor */
    UPROPERTY(EditInstanceOnly, Category = "DMX")
    TObjectPtr<ADMXControlConsoleActor> ControlConsoleActor;

    /** 是否自动开始发送 DMX */
    UPROPERTY(EditAnywhere, Category = "DMX")
    bool bAutoStart = true;
};
```

**MyDMXController.cpp**

```cpp
#include "MyDMXController.h"
#include "DMXControlConsoleActor.h"
#include "DMXControlConsoleData.h"
#include "DMXControlConsoleFaderGroup.h"
#include "DMXControlConsoleFaderBase.h"

AMyDMXController::AMyDMXController()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDMXController::BeginPlay()
{
    Super::BeginPlay();

    if (!ControlConsoleActor)
    {
        UE_LOG(LogTemp, Warning, TEXT("MyDMXController: No ControlConsoleActor assigned"));
        return;
    }

    // 验证控制台数据
    UDMXControlConsoleData* ConsoleData = ControlConsoleActor->GetControlConsoleData();
    if (!ConsoleData)
    {
        UE_LOG(LogTemp, Warning, TEXT("MyDMXController: No ConsoleData found"));
        return;
    }

    // 监听 Fader Group 添加事件
    ConsoleData->GetOnFaderGroupAdded().AddLambda(
        [](const UDMXControlConsoleFaderGroup* Group)
        {
            UE_LOG(LogTemp, Log, TEXT("Fader Group added: %s"), *Group->GetFaderGroupName());
        });

    // 自动开始发送
    if (bAutoStart)
    {
        ControlConsoleActor->StartSendingDMX();
        UE_LOG(LogTemp, Log, TEXT("MyDMXController: Started sending DMX"));
    }
}

void AMyDMXController::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (ControlConsoleActor)
    {
        ControlConsoleActor->StopSendingDMX();
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从 `DMXControlConsole.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | DMX 协议层，用于 Output Port 发送 |
| `DMXRuntime` / `DMXEngine` | DMX 核心运行时，Fixture Patch / Fixture Library 等 |
| `DMXBlueprintGraph` | DMX 蓝图图节点（运行时需要读取 Fixture Function 定义） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | VP 资产分类重组，插件归类到新的资产路径 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复前一次提交中错误的查找替换操作 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退之前的提交 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 适配引擎 API 变更，修复委托注册问题 |

### 维护评价

- **创建时间**：2023 年 3 月，约 3 年历史
- **更新频率**：活跃维护中，最近 3 个月内有多次更新
- **更新内容**：主要是编译警告修复和引擎 API 适配，属于维护性更新
- **已知状态**：从实验性插件演变为正式插件，已集成到 Virtual Production 流水线中
- **注意事项**：该插件有独立的自定义序列化版本（`FDMXControlConsoleMainStreamObjectVersion`），5.5 版本进行了 Fader Group 向 Fixture Patch Ref 的升级迁移
- **推荐程度**：✅ 推荐使用。作为 Epic 官方 Virtual Production 工具链的一部分，持续维护且已脱离实验状态，适合生产环境使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXControlConsole)
- [官方文档]()（无）