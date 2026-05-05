# DMX Control Console

> Console that can be patched from DMX Libraries and sends DMX to Output Ports（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXControlConsole` (Runtime), `DMXControlConsoleEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXControlConsole) | |

## 用途

DMX Control Console 插件为 Unreal Engine 提供了一个功能完整的 DMX 控制台。它解决的核心问题是：在虚拟制作（Virtual Production）场景中，需要一种直观、可配置的方式来实时控制 DMX 设备（如灯光、特效设备等）。

该插件允许用户基于一个 `DMXLibrary` 资产来配置控制台。控制台由多个“推子组”（Fader Group）构成，每个推子组可以对应一个 DMX 灯具补丁（Fixture Patch）或一组原始 DMX 通道。用户可以通过图形界面（编辑器）或蓝图来调整每个推子的值，这些值会被实时转换为 DMX 信号，并发送到指定的输出端口（Output Port），从而控制物理或虚拟的 DMX 设备。

其存在意义在于将复杂的 DMX 协议和设备配置封装成一个易于使用的控制面板，极大地简化了在 UE 内进行灯光编程和实时控制的工作流程。

## 使用场景

-   **影视虚拟制作**：在 LED 虚拟影棚中，你需要实时调整场景内虚拟灯光的亮度、颜色、图案等参数，以匹配实拍演员的光照环境。
-   **现场活动与演出**：在 UE 中预演或控制一场灯光秀，通过控制台快速触发不同的灯光场景（Cue）。
-   **建筑可视化与主题公园**：需要精确控制大量 DMX 灯具来营造特定氛围，并希望通过蓝图逻辑实现自动化控制。
-   **任何需要与 Art-Net, sACN 等 DMX-over-Ethernet 协议设备交互的场景**。

## 蓝图用法

该插件的核心蓝图接口主要通过 `ADMXControlConsoleActor` 暴露，用于控制 DMX 的发送和控制台状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Sending DMX` | 开始发送 DMX 数据 | `ADMXControlConsoleActor` |
| `Stop Sending DMX` | 停止发送 DMX 数据 | `ADMXControlConsoleActor` |
| `Pause Sending DMX` | 暂停发送 DMX 数据 | `ADMXControlConsoleActor` |
| `Reset To Default` | 将所有推子重置为默认值 | `ADMXControlConsoleActor` |
| `Reset To Zero` | 将所有推子值重置为 0 | `ADMXControlConsoleActor` |
| `Set Value` | 设置单个推子的当前值 | `UDMXControlConsoleFaderBase` |
| `Set Min Value` | 设置推子的最小值 | `UDMXControlConsoleFaderBase` |
| `Set Max Value` | 设置推子的最大值 | `UDMXControlConsoleFaderBase` |
| `Set Enabled` | 启用或禁用一个推子 | `UDMXControlConsoleFaderBase` |
| `Set Locked` | 锁定或解锁一个推子（防止值被修改） | `UDMXControlConsoleFaderBase` |
| `Reset To Default` | 将单个推子重置为其默认值 | `UDMXControlConsoleFaderBase` |

### 使用示例（蓝图描述）

1.  **基础控制**：在关卡中放置一个 `ADMXControlConsoleActor`。在蓝图中，获取该 Actor 的引用，然后调用 `Start Sending DMX` 节点即可开始发送数据。通常会在 `BeginPlay` 事件中调用。
2.  **动态调整推子**：要控制某个特定推子，你需要先获取到它的引用。这通常通过遍历 `UDMXControlConsoleData` -> `FaderGroupRows` -> `FaderGroups` -> `Elements` -> `Faders` 来实现。获得 `UDMXControlConsoleFaderBase` 对象后，即可调用 `Set Value` 等节点。
3.  **场景切换**：你可以创建多个不同的 `DMXControlConsole` 资产（`.dmxcontrolconsole`），每个资产配置不同的推子布局和默认值。在运行时，通过 `ADMXControlConsoleActor` 的 `Set DMX Control Console Data` 函数（C++接口）来切换不同的控制台配置，实现灯光场景的快速切换。

## C++ 用法

### 头文件引入

```cpp
#include "DMXControlConsole.h"
#include "DMXControlConsoleData.h"
#include "DMXControlConsoleFaderGroup.h"
#include "DMXControlConsoleFaderBase.h"
#include "DMXControlConsoleActor.h"
```

### 基本用法

以下代码演示了如何在 C++ 中程序化地创建和操作一个 DMX 控制台。

```cpp
// 假设你已经有了一个 UDMXLibrary* MyDMXLibrary;
// 创建一个控制台数据对象
UDMXControlConsoleData* ConsoleData = NewObject<UDMXControlConsoleData>();

// 设置要使用的 DMX 库
ConsoleData->SetDMXLibrary(MyDMXLibrary);

// 基于 DMX 库自动生成推子组
ConsoleData->GenerateFromDMXLibrary();

// 获取第一个推子组
const TArray<UDMXControlConsoleFaderGroupRow*>& Rows = ConsoleData->GetFaderGroupRows();
if (Rows.Num() > 0 && Rows[0]->GetFaderGroups().Num() > 0)
{
    UDMXControlConsoleFaderGroup* FirstGroup = Rows[0]->GetFaderGroups()[0];
    
    // 获取该组下的所有推子
    TArray<UDMXControlConsoleFaderBase*> Faders = FirstGroup->GetAllFaders();
    if (Faders.Num() > 0)
    {
        // 设置第一个推子的值为 128 (0-255 范围)
        Faders[0]->SetValue(128);
    }
}

// 将控制台数据应用到场景中的 Actor
ADMXControlConsoleActor* ConsoleActor = GetWorld()->SpawnActor<ADMXControlConsoleActor>();
ConsoleActor->SetDMXControlConsoleData(ConsoleData);
ConsoleActor->StartSendingDMX();
```

### 进阶用法

结合 Cue Stack（提示栈）功能，可以实现灯光场景的录制与回放。

```cpp
// 获取控制台的提示栈
UDMXControlConsoleCueStack* CueStack = ConsoleData->GetCueStack();
if (CueStack)
{
    // 收集当前所有推子
    TArray<UDMXControlConsoleFaderBase*> AllFaders;
    for (const UDMXControlConsoleFaderGroupRow* Row : ConsoleData->GetFaderGroupRows())
    {
        for (UDMXControlConsoleFaderGroup* Group : Row->GetFaderGroups())
        {
            AllFaders.Append(Group->GetAllFaders());
        }
    }

    // 将当前状态保存为一个名为 “Scene1” 的提示
    FDMXControlConsoleCue* NewCue = CueStack->AddNewCue(AllFaders, TEXT("Scene1"));
    
    // ... 修改一些推子的值 ...
    
    // 稍后，可以回忆这个提示来恢复状态
    if (NewCue)
    {
        CueStack->Recall(*NewCue);
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个自定义 Actor 来驱动 DMX 控制台。

**MyDMXController.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDMXController.generated.h"

class ADMXControlConsoleActor;
class UDMXControlConsoleData;
class UDMXLibrary;

UCLASS()
class AMyDMXController : public AActor
{
    GENERATED_BODY()

public:
    AMyDMXController();

protected:
    virtual void BeginPlay() override;

    // 要使用的 DMX 库资产
    UPROPERTY(EditAnywhere, Category = "DMX")
    TObjectPtr<UDMXLibrary> DMXLibraryAsset;

private:
    UPROPERTY()
    TObjectPtr<ADMXControlConsoleActor> ConsoleActor;

    UPROPERTY()
    TObjectPtr<UDMXControlConsoleData> ConsoleData;
};
```

**MyDMXController.cpp**
```cpp
#include "MyDMXController.h"
#include "DMXControlConsoleActor.h"
#include "DMXControlConsoleData.h"
#include "DMXLibrary.h"

AMyDMXController::AMyDMXController()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDMXController::BeginPlay()
{
    Super::BeginPlay();

    if (!DMXLibraryAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("MyDMXController: No DMX Library assigned!"));
        return;
    }

    // 1. 创建控制台数据
    ConsoleData = NewObject<UDMXControlConsoleData>(this);
    ConsoleData->SetDMXLibrary(DMXLibraryAsset);
    ConsoleData->GenerateFromDMXLibrary();

    // 2. 生成控制台 Actor
    ConsoleActor = GetWorld()->SpawnActor<ADMXControlConsoleActor>();
    ConsoleActor->SetDMXControlConsoleData(ConsoleData);

    // 3. 开始发送 DMX
    ConsoleActor->StartSendingDMX();

    UE_LOG(LogTemp, Log, TEXT("MyDMXController: DMX Console started with library '%s'."), *DMXLibraryAsset->GetName());
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下模块（在 `.Build.cs` 文件中添加）：

| 模块 | 用途 |
|---|---|
| `DMXControlConsole` | 插件的核心运行时模块，包含所有数据模型和逻辑。 |
| `DMX` | DMX 核心框架，提供协议、实体、库等基础类型。 |
| `DMXProtocol` | DMX 协议实现（如 Art-Net, sACN），用于实际发送数据。 |

## 维护状态

### 近期更新

```
- ed12aec9a262 DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate
  (代码清理，将 FORCEINLINE 替换为 inline，属于内部优化。)
- 06eb4dc3d3e1 DMX: Fix Control Console cannot use patches that were created in a DMX Library while the Control Console is not loaded, fix Control Console shows patches that were deleted while Control Console was not loaded
  (修复了两个重要Bug：1. 控制台无法使用在其未加载时于DMX库中创建的补丁；2. 控制台会显示在其未加载时已被删除的补丁。)
- 944844853e9f DMX Control Console: Fix issues where DMX Control Console Actor did not send DMX in certain setups.
  (修复了控制台 Actor 在某些配置下不发送 DMX 的问题。)
```

### 维护评价

**活跃维护**。该插件创建于 2023 年 3 月，至今约 2 年，属于较新的插件。从最近的 git 历史看，维护非常活跃，最近一次提交在 2025 年 10 月，且提交内容均为实质性的 Bug 修复和代码质量改进，而非简单的编译适配。这表明 Epic Games 团队仍在积极维护和改进此插件。

**推荐使用**。作为官方 Virtual Production 工具链的一部分，DMX Control Console 提供了稳定、功能完整的 DMX 控制解决方案。其与 DMX Library 的深度集成、支持 Cue Stack 等高级功能，使其成为在 UE 内进行专业灯光控制的首选工具。对于有 DMX 控制需求的项目，强烈推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXControlConsole)
- [官方文档]() (暂无)
- [测试用例]() (暂无)