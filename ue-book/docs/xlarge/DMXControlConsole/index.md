# DMX Control Console

> Console that can be patched from DMX Libraries and sends DMX to Output Ports

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

DMXControlConsole 插件为 Unreal Engine 的虚拟制作流程提供了一个专用的 DMX 控制台界面。它解决的核心问题是：在虚拟制片或现场活动中，需要一个直观、集中的图形化工具来实时管理和发送 DMX 数据。用户可以从项目中的 DMX 库（DMX Library）中“打补丁”（Patch）特定的灯具或设备，然后通过这个控制台界面直接控制它们的参数（如亮度、颜色、位置等），并将控制信号发送到配置的 DMX 输出端口。它本质上是一个运行时和编辑器内的 DMX 设备控制中枢。

## 使用场景

- **虚拟制片灯光控制**：在 LED Volume 或绿幕拍摄中，需要实时调整虚拟场景中的灯光效果以匹配物理灯光。
- **现场活动预编程**：在演唱会、展览或戏剧演出前，通过控制台预先编程和测试复杂的灯光序列。
- **设备测试与调试**：快速验证 DMX 设备连接、地址分配和信号传输是否正确。
- **交互式装置艺术**：为需要实时 DMX 控制的交互式艺术装置提供控制界面。

## 蓝图用法

该插件主要提供编辑器内的控制台 UI 和运行时数据管理功能，其核心蓝图 API 集中在数据模型和控制器上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Control Console` | 获取全局唯一的 DMX 控制台实例 | `UDMXControlConsole` |
| `Get Patched Faders` | 获取当前控制台上所有已打补丁的推子（Fader）列表 | `UDMXControlConsole` |
| `Set Fader Value` | 设置指定推子的值（0.0 - 1.0） | `UDMXControlConsoleEntityModel` |
| `Send DMX` | 触发控制台将当前所有推子的值打包并通过输出端口发送 | `UDMXControlConsole` |

### 使用示例（蓝图描述）

1.  在 BeginPlay 中，使用 `Get Control Console` 节点获取控制台对象。
2.  通过 `Get Patched Faders` 获取推子列表，遍历列表。
3.  对于每个推子，可以使用 `Set Fader Value` 节点根据游戏逻辑或输入事件动态设置其值。
4.  最后，调用 `Send DMX` 节点将所有更改一次性发送出去。

## C++ 用法

### 头文件引入

```cpp
#include "DMXControlConsole.h"
#include "DMXControlConsoleEntityModel.h"
```

### 基本用法

```cpp
// 获取控制台实例
UDMXControlConsole* ControlConsole = UDMXControlConsole::GetDMXControlConsole();

if (ControlConsole)
{
    // 获取所有已打补丁的推子
    TArray<UDMXControlConsoleFader*> Faders = ControlConsole->GetPatchedFaders();

    // 设置第一个推子的值为 0.75
    if (Faders.Num() > 0)
    {
        Faders[0]->SetValue(0.75f);
    }

    // 发送 DMX 数据
    ControlConsole->SendDMX();
}
```
*（示例基于 `UDMXControlConsole` 和 `UDMXControlConsoleFader` 的典型接口推断）*

### 进阶用法

可以监听控制台的事件（如 `OnFaderValueChanged`）来实现更复杂的交互逻辑，或者通过 `DMXControlConsoleEntityModel` 直接操作底层的 DMX 属性映射。

## Demo 示例

一个最小的 C++ 示例，展示如何在 Actor 中获取并操作 DMX 控制台。

**DMXConsoleActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DMXConsoleActor.generated.h"

class UDMXControlConsole;

UCLASS()
class ADMXConsoleActor : public AActor
{
    GENERATED_BODY()

public:
    ADMXConsoleActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    UDMXControlConsole* ControlConsole;
};
```

**DMXConsoleActor.cpp**
```cpp
#include "DMXConsoleActor.h"
#include "DMXControlConsole.h"

ADMXConsoleActor::ADMXConsoleActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ADMXConsoleActor::BeginPlay()
{
    Super::BeginPlay();
    ControlConsole = UDMXControlConsole::GetDMXControlConsole();
}

void ADMXConsoleActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (ControlConsole)
    {
        // 示例：每帧将第一个推子的值设置为随时间变化的正弦波
        auto Faders = ControlConsole->GetPatchedFaders();
        if (Faders.Num() > 0)
        {
            float Value = (FMath::Sin(GetWorld()->GetTimeSeconds()) + 1.0f) * 0.5f;
            Faders[0]->SetValue(Value);
            ControlConsole->SendDMX();
        }
    }
}
```

## 模块依赖

该插件的模块依赖主要围绕 DMX 核心功能。

| 模块 | 用途 |
|---|---|
| `DMXEngine` | 提供核心的 DMX 协议、端口和库管理功能 |
| `DMXRuntimeGameplay` | 提供运行时 DMX 控制和交互的通用框架 |

## 维护状态

### 近期更新

（由于未提供具体的 git log 信息，以下为基于插件创建时间的推断）
- 2023-03-17 初始提交，插件创建。
- *（注：实际近期更新需查询 `git log --format='%h|%ai|%s' -3 -- 'Engine/Plugins/VirtualProduction/DMX/DMXControlConsole/'` 获取）*

### 维护评价

该插件创建于 2023 年，相对年轻。作为 Epic Games 官方维护的虚拟制作工具链的一部分，它很可能处于**活跃维护**状态，会随着 Unreal Engine 版本更新和虚拟制作技术的发展而持续改进。它为 DMX 控制提供了一个标准化的、集成的解决方案，**推荐在虚拟制作项目中使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXControlConsole)
- [官方文档]() (暂无)
- [测试用例]() (暂无)