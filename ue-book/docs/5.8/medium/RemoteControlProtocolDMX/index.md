# Remote Control Protocol DMX

> Allows interactions between DMX and RemoteControl API.

| 属性 | 值 |
|---|---|
| 中文名 | DMX 远程控制协议 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、插件配置） |
| 模块 | `RemoteControlProtocolDMX` (Runtime), `RemoteControlProtocolDMXEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolDMX) | |

## 用途

本插件是**DMX 协议**与**虚幻引擎远程控制 API (Remote Control)** 之间的桥梁。它允许外部 DMX 控制台或软件（如灯光控台）通过标准的 Art-Net 或 sACN 协议，实时读取和控制引擎内的各种属性（如 Actor 位置、材质参数、光源强度等）。这主要应用于**虚拟制作 (Virtual Production)** 和**现场演出 (Live Events)** 场景，实现物理世界灯光控制与虚拟场景的同步。

## 使用场景

- **虚拟制片**：在 LED 虚拟影棚中，使用真实的灯光控台（DMX）精确控制虚幻场景中与实体灯光对应的虚拟光源参数，确保光影匹配。
- **现场演出**：在演唱会、舞台剧中，通过 DMX 协议触发引擎内的特效、改变场景颜色或移动虚拟物体。
- **主题公园/互动装置**：将 DMX 信号作为输入，控制虚幻引擎驱动的大型投影、LED 墙或交互式装置的内容变化。

## 蓝图用法

本插件主要通过 Remote Control Preset 和专用蓝图节点暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Map DMX Channel` | 将一个 DMX 通道（Universe, Channel）映射到一个可远程控制的引擎属性 | `URemoteControlDMXLibrary` |
| `Send DMX Value` | 向特定的 DMX 通道发送一个值（0-255） | `URemoteControlDMXLibrary` |
| `Get DMX Value` | 从特定的 DMX 通道读取一个值 | `URemoteControlDMXLibrary` |
| `Set Protocol Settings` | 配置 DMX 协议连接参数（如 Art-Net IP、端口） | `URemoteControlDMXSettings` |

### 使用示例

1.  **准备**：确保 `RemoteControl` 和 `DMXProtocol`、`DMXEngine` 插件已启用。
2.  **创建 Preset**：在内容浏览器中创建“远程控制预设 (Remote Control Preset)”。
3.  **映射属性**：打开预设，选中一个对象（如一个点光源），将其“强度”属性添加到预设中。然后使用 `Map DMX Channel` 节点，将该属性与 DMX Universe 1 的 Channel 1 关联。
4.  **运行**：启动项目，连接你的 DMX 控制台。在控台上推高 Channel 1 的推子，场景中对应点光源的强度就会实时变化。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteControlProtocolDMX.h"
// 包含 RemoteControl 和 DMX 核心头文件
#include "RemoteControlSettings.h"
#include "DMXProtocolModule.h"
```

### 基本用法

从测试用例提取的代码示例，展示如何在 C++ 中设置 DMX 绑定。

```cpp
// 来源: Tests/RemoteControlProtocolDMXTest.cpp
// 假设已经获取到一个 URemoteControlPreset* Preset 和一个 DMX 库

// 获取协议实例
IDMXProtocolPtr DMXProtocol = FDMXProtocolModule::Get().GetProtocol(FName(TEXT("Art-Net")));
if (DMXProtocol.IsValid())
{
    // 创建一个 DMX 到属性的绑定
    FRCDMXProtocolBinding Binding;
    Binding.DMXProtocol = DMXProtocol->GetProtocolName();
    Binding.DMXUniverse = 1;
    Binding.DMXChannel = 1;
    Binding.MappingType = ERCDMXMappingType::Absolute;

    // 将绑定应用到预设中的某个可暴露属性（如光照强度）
    FGuid PropertyId = Preset->GetPropertyId(TEXT("Intensity")); // 示例
    Preset->AddProtocolBinding(PropertyId, Binding);

    // 应用绑定，开始监听 DMX 数据
    Preset->Apply();
}
```

### 进阶用法

结合 Remote Control API，动态创建和管理 DMX 映射。

```cpp
// 动态添加一个被控对象和属性，然后绑定 DMX
UObject* ActorToControl = ...; // 获取需要控制的 Actor
FRCFieldPathInfo FieldPath(TEXT("LightComponent.Intensity"));
FProperty* PropertyToControl = FieldPath.Resolve(ActorToControl).Property;

// 将属性添加到预设
FRCObjectReference ObjectRef;
ObjectRef.Object = ActorToControl;
ObjectRef.PropertyPath = FieldPath;
FRCFieldDescriptor Descriptor = Preset->AddObjectProperties(ObjectRef);

// 创建 DMX 绑定并应用
FRCDMXProtocolBinding Binding;
// ... 配置 Binding ...
Preset->AddProtocolBinding(Descriptor.Id, Binding);
Preset->Apply();
```

## Demo 示例

一个最小化的 Actor，通过 DMX 控制其旋转。

**DMXControlledActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DMXControlledActor.generated.h"

UCLASS()
class ADMXControlledActor : public AActor
{
    GENERATED_BODY()
    
public:
    ADMXControlledActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(BlueprintReadWrite, EditAnywhere)
    FRotator TargetRotation;

    UPROPERTY()
    class URemoteControlPreset* ControlPreset;

    void OnDMXChannelUpdated(const struct FDMXAttributeName& AttributeName, int32 Value);
};
```

**DMXControlledActor.cpp**
```cpp
#include "DMXControlledActor.h"
#include "RemoteControlPreset.h"
#include "RemoteControlProtocolDMX.h"
#include "DMXProtocolModule.h"

ADMXControlledActor::ADMXControlledActor()
{
    PrimaryActorTick.bCanEverTick = false;
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
}

void ADMXControlledActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建或获取一个远程控制预设 (通常在编辑器中创建)
    ControlPreset = NewObject<URemoteControlPreset>(this, TEXT("MyDMXPreset"));

    // 2. 添加要控制的属性 (这里控制 Actor 的 Yaw 旋转)
    FRCObjectReference Ref;
    Ref.Object = this;
    Ref.PropertyPath = FRCFieldPathInfo(TEXT("TargetRotation.Yaw"));
    FRCFieldDescriptor Desc = ControlPreset->AddObjectProperties(Ref);

    // 3. 绑定到 DMX 通道 (Universe 1, Channel 10)
    FRCDMXProtocolBinding Binding;
    Binding.DMXProtocol = FName("Art-Net");
    Binding.DMXUniverse = 1;
    Binding.DMXChannel = 10;
    Binding.MappingType = ERCDMXMappingType::Absolute;
    Binding.ScaleFactor = 1.0f; // 可调整映射范围

    ControlPreset->AddProtocolBinding(Desc.Id, Binding);

    // 4. 应用并开始监听
    ControlPreset->Apply();

    // (可选) 直接绑定一个更新回调，用于即时响应
    // ControlPreset->OnObjectPropertyChanged.AddUObject(this, &ADMXControlledActor::OnDMXChannelUpdated);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 核心远程控制 API，提供预设和属性暴露功能 |
| `DMXProtocol` | 提供 DMX 协议的运行时支持（如 Art-Net， sACN） |
| `DMXEngine` | 提供 DMX 数据的上层封装和管理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏迁移至新版 `UE_LOGF`， 修复编译警告。 |
| 2025-09-16 | `77ee7eae` | Motion Design: removed beta tag from motion design plugins. | 移除了 Motion Design 插件的 Beta 标记， 标志着其稳定。 |
| 2025-04-09 | `5b3f195a` | Remote Control: Fixed issue with re-applying signatures clearing the DMX Library | 修复了重新应用签名时错误清空 DMX 库的关键 Bug。 |
| 2025-04-03 | `9fc06e81` | Remote Control: Add struct referenced objects to protocol bindings to consider protocol entity | 增强了协议绑定， 使其能考虑结构体内的引用对象。 |
| 2025-04-03 | `e232a05a` | Remote Control: fixed issue where the protocols kept running even after the RC asset window was closed | 修复了关闭远程控制资产窗口后协议仍在运行的资源泄漏问题。 |

### 维护评价

该插件**仍在积极维护中**。近期（2025-2026年）有多次重要的 Bug 修复和功能增强，特别是修复了与 DMX 库和协议生命周期相关的稳定性问题。尽管其首次提交于 2021 年（约 5 年前），但作为虚拟制作核心管线的一部分，它持续获得 Epic 的关注和更新。对于需要集成 DMX 硬件控制的虚拟制作项目，**可以放心使用**。主要限制是它需要 `DMXProtocol` 和 `RemoteControl` 等上游插件支持，整体集成链较长。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolDMX)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolDMX/Tests)