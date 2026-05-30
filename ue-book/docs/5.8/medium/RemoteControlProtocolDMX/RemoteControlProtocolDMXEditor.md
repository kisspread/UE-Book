# Remote Control Protocol DMX

> Allows interactions between DMX and RemoteControl API.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制 DMX 协议 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产） |
| 模块 | `RemoteControlProtocolDMX` (Runtime), `RemoteControlProtocolDMXEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolDMX) | |

## 用途

此插件为 Unreal Engine 的远程控制系统（Remote Control）提供了 DMX 协议支持。它解决了虚拟制片（Virtual Production）中，需要通过标准灯光控制台（使用 DMX 协议）实时控制引擎内对象属性的需求。

具体来说，它在引擎内部搭建了一个桥梁：
1.  **映射关系**：将通过 Remote Control API 暴露的任意属性（如灯光强度、颜色、Actor 位置、材质参数等）映射到 DMX 信号的特定地址（Universe 和 Channel）。
2.  **双向交互**：支持从外部 DMX 控制台发送信号控制引擎内的属性，也支持将引擎内属性的变化发送到 DMX 网络。
3.  **自动化管理**：提供了自动创建和配置 DMX Library（包含 Fixture Types 和 Fixture Patches）的功能，简化了设置流程，使得暴露属性的过程更加便捷。

## 使用场景

-   **虚拟制片灯光控制**：使用 GrandMA、ChamSys 等专业灯光控制台，通过 DMX 协议精确控制 Unreal 场景中灯光的亮度、颜色、角度等。
-   **交互式装置**：将物理世界的 DMX 控制设备（如推杆、旋钮）映射到虚拟场景中的交互元素。
-   **舞台预演**：在虚拟环境中预先编程灯光效果，然后将 DMX 数据导出到真实灯光控制台进行现场演出。
-   **数据监控与记录**：将引擎中某个实时变化的数据（如玩家位置、音频响度）转换为 DMX 信号，发送给外部显示或记录设备。

## 蓝图用法

此插件的核心功能主要通过 Remote Control API 和编辑器界面进行配置，不直接暴露大量 `BlueprintCallable` 节点。配置完成后，属性绑定在运行时自动处理。

### 核心节点

由于主要功能是协议集成和编辑器扩展，无直接蓝图节点。

### 使用示例（蓝图描述）

1.  **配置阶段（编辑器内完成）**：
    *   在 Remote Control Panel 中，选中一个 `Remote Control Preset`。
    *   在该 Preset 的属性面板中，找到 `DMX User Data` 部分（由本插件添加）。
    *   启用自动补丁（Auto Patch）或手动选择/创建一个 DMX Library。
    *   将需要控制的属性（如一个 Light 的 `Intensity`）通过 Remote Control 暴露。
    *   插件会自动或手动为该属性分配一个 DMX 地址（Universe + Channel）。
2.  **运行阶段**：
    *   外部 DMX 控制台发送对应地址的信号。
    *   引擎内对应属性的值会自动更新。
    *   同理，当引擎内该属性值变化时，对应的 DMX 信号也会被发送出去。

## C++ 用法

此插件的 C++ 接口主要面向需要深度集成或定制 DMX 映射逻辑的开发者。核心逻辑由 `RemoteControlProtocolDMX` (Runtime) 模块实现，编辑器 UI 由 `RemoteControlProtocolDMXEditor` 模块实现。

### 头文件引入

```cpp
#include "RemoteControlProtocolDMX.h" // 对于运行时接口
#include "RemoteControlDMXLibraryBuilder.h" // 对于编辑器库构建
```

### 基本用法

此插件通常不直接实例化其核心类，而是通过 Remote Control 系统进行交互。一个关键的编辑器时操作是通过 `FRemoteControlDMXLibraryBuilder` 管理 DMX 库。

```cpp
// 示例：获取某个 Remote Control Preset 关联的 DMX 用户数据 (编辑器代码)
// 来源: RemoteControlDMXLibraryBuilder.h
#include "RemoteControlPreset.h"
#include "RemoteControlDMXUserData.h"

void DoSomethingWithDMXUserdata(URemoteControlPreset* Preset)
{
    if (Preset)
    {
        // 获取或创建与这个 Preset 关联的 DMX 用户数据
        URemoteControlDMXUserData* DMXUserData = Preset->FindOrAddCustomData<URemoteControlDMXUserData>();
        if (DMXUserData)
        {
            // 例如，检查自动补丁设置
            bool bIsAutoPatchEnabled = DMXUserData->bAutoPatch;
            UE_LOG(LogTemp, Log, TEXT("Auto Patch is %s for Preset %s"), bIsAutoPatchEnabled ? TEXT("enabled") : TEXT("disabled"), *Preset->GetName());
        }
    }
}
```

### 进阶用法

理解插件的自动绑定机制。`FRemoteControlDMXAutoBindHandler` 是一个 tickable 对象，它监听 DMX 输入端口的信号，并根据已配置的协议实体（Protocol Entities）更新对应的引擎属性。

```cpp
// 概念性示例：自动绑定处理流程 (内部机制，通常无需直接调用)
// 来源: RemoteControlDMXAutoBindHandler.h
#include "DMXInputPort.h"
#include "DMXSignal.h"

void OnDMXSignalReceived(const TSharedRef<FDMXInputPort>& InputPort, const TSharedRef<FDMXSignal>& Signal)
{
    // 插件内部的 FRemoteControlDMXAutoBindHandler 会执行类似逻辑：
    // 1. 查找所有使用了该 InputPort 的 RemoteControlProtocolDMX 协议实体。
    // 2. 遍历协议实体，根据其配置的 Universe/Channel 从 Signal 中提取数据。
    // 3. 使用提取的数据（可能经过类型转换和缩放）更新对应的引擎属性。
    // 4. 反向地，当引擎属性变化时，也可能通过协议实体生成 Signal 并通过 OutputPort 发送。
    // 此过程由插件在引擎运行时自动完成，开发者通常无需干预。
}
```

## Demo 示例

以下示例展示如何在 C++ 中访问与一个 `RemoteControlPreset` 关联的 DMX 设置，这是与该插件交互的常见起点。

```cpp
// MyDMXHelper.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyDMXHelper.generated.h"

class URemoteControlPreset;
class URemoteControlDMXUserData;

UCLASS()
class UMyDMXHelper : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    // 初始化时可能需要的逻辑
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    // 获取某个预设的DMX配置信息（例如用于UI显示）
    UFUNCTION(BlueprintPure, Category = "DMX")
    bool GetDMXConfigForPreset(URemoteControlPreset* Preset, bool& bOutAutoPatch, int32& OutStartUniverse) const;
};
```

```cpp
// MyDMXHelper.cpp
#include "MyDMXHelper.h"
#include "RemoteControlPreset.h"
#include "RemoteControlDMXUserData.h"

void UMyDMXHelper::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    // 这里可以进行一些与DMX插件相关的全局初始化，但通常插件自身已处理。
}

bool UMyDMXHelper::GetDMXConfigForPreset(URemoteControlPreset* Preset, bool& bOutAutoPatch, int32& OutStartUniverse) const
{
    if (!Preset)
    {
        return false;
    }

    const URemoteControlDMXUserData* DMXUserData = Preset->FindCustomData<URemoteControlDMXUserData>();
    if (DMXUserData)
    {
        bOutAutoPatch = DMXUserData->bAutoPatch;
        OutStartUniverse = DMXUserData->AutoAssignFromUniverse;
        return true;
    }
    
    return false;
}
```

## 模块依赖

使用此插件时，你的模块通常不需要直接依赖它，因为它的主要功能是通过 Remote Control 框架和 DMX 引擎插件提供。但是，如果你需要在自己的 C++ 代码中访问其暴露的类（如 `URemoteControlDMXUserData`），则需要添加对 `RemoteControl` 和 `DMXEngine` 模块的依赖。

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 远程控制核心 API 和框架 |
| `DMXEngine` | DMX 引擎，提供 DMX Library、Fixture Type、Fixture Patch 等核心数据资产 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 统一日志格式，迁移至新的日志宏 |
| 2025-09-16 | `77ee7eae` | Motion Design: removed beta tag from motion design plugins. | 移除了 Motion Design 插件的 beta 标签（关联提交） |
| 2025-04-09 | `5b3f195a` | Remote Control: Fixed issue with re-applying signatures clearing the DMX Library | 修复重新应用签名时会错误清除关联 DMX 库的问题 |
| 2025-04-03 | `9fc06e81` | Remote Control: Add struct referenced objects to protocol bindings to consider protocol entity | 增强协议绑定，确保考虑结构体中引用的对象 |
| 2025-04-03 | `e232a05a` | Remote Control: fixed issue where the protocols kept running even after the RC asset window was clos | 修复了 Remote Control 资产窗口关闭后协议仍在后台运行的问题 |

### 维护评价

该插件自 2021 年创建以来，至今已有约 5 年历史。从 Git 历史来看，它在 **2025 年 4 月** 仍有实质性更新，修复了两个重要的运行时和编辑器交互问题，表明它仍处于 **维护中** 状态，并针对虚拟制片工作流进行了优化和问题修复。

**推荐使用**：对于需要在虚拟制片中集成 DMX 控制的团队，此插件是官方提供的标准解决方案，其功能经过验证且仍在修复缺陷。尽管更新不频繁，但已解决了主要的已知问题。需要注意的是，它默认未启用（`EnabledByDefault: false`），因此需要在项目设置或插件管理器中手动启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolDMX)
-   [官方文档]()（暂无）