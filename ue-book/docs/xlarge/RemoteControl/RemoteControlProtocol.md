# Remote Control Protocol

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControl` (Runtime), `RemoteControlCommon` (Runtime), `RemoteControlLogic` (Runtime), `RemoteControlMultiUser` (Runtime), `RemoteControlProtocol` (Runtime), `RemoteControlProtocolWidgets` (Runtime), `RemoteControlUI` (Runtime), `WebRemoteControl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl) | |

## 用途

Remote Control Protocol 模块是 Remote Control API 插件的核心协议抽象层。它本身不实现具体的通信协议（如 DMX、MIDI、OSC），而是为这些协议的集成提供一个标准化的框架。其核心价值在于：

1.  **协议抽象**：定义了 `IRemoteControlProtocol` 接口，任何具体的远程控制协议（如 DMX）都需要实现此接口，从而被 Remote Control 系统统一管理和调度。
2.  **实体管理**：通过 `FRemoteControlProtocolEntity` 和 `FRemoteControlProtocolBinding` 等结构，将引擎内的属性（如 Actor 的位置、材质参数）与外部协议的值进行绑定。
3.  **值映射与队列**：提供了将外部协议输入值映射到引擎属性值范围的功能，并通过队列机制（`QueueValue`, `OnBeginFrame`）确保在游戏线程安全地应用这些值。
4.  **编辑器集成**：为协议在 Remote Control Panel 中的显示提供了列（Column）注册机制，方便用户查看和编辑协议绑定。

简而言之，这个模块是连接外部控制设备/软件与虚幻引擎内部属性的“翻译官”和“调度中心”。

## 使用场景

-   **虚拟制片**：在 LED Volume 拍摄中，通过 DMX 协议远程控制场景灯光、摄像机参数或虚拟资产。
-   **现场演出**：使用 MIDI 控制器或自定义硬件实时调整引擎内的视觉效果、音频参数。
-   **自动化测试与集成**：通过自定义的 HTTP 或 WebSocket 协议，从外部脚本或应用程序控制引擎，用于自动化测试或构建复杂的交互系统。
-   **开发自定义协议**：如果你需要将一种新的硬件协议（如某种工业总线）集成到虚幻引擎中，可以基于此模块快速开发，而无需从头构建整个远程控制管线。

## 蓝图用法

本模块主要为 C++ 协议实现提供基础，直接暴露给蓝图的节点较少。主要的蓝图交互点在于配置协议绑定。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FRCSignatureProtocolAction` (结构体) | 在 Remote Control Preset 的签名（Signature）系统中定义协议动作。可在蓝图编辑器中配置协议名称、映射空间（Additive/Multiply/Absolute）和具体的映射范围。 | `FRCSignatureProtocolAction` |

### 使用示例（蓝图描述）

在 Remote Control Preset 资产的编辑器界面中，你可以为暴露的属性添加一个“Protocol Action”。在细节面板中：
1.  从 `ProtocolName` 下拉菜单选择已注册的协议（如 “DMX”）。
2.  在 `ProtocolEntity` 中配置该协议特定的参数（如 DMX 的 Universe 和 Channel）。
3.  设置 `MappingSpace` 来决定外部值如何影响属性值（叠加、相乘或绝对覆盖）。
4.  在 `Mappings` 中定义输入值（如 DMX 的 0-255）到属性值范围（如灯光的 0-100 亮度）的映射曲线。

## C++ 用法

### 头文件引入

```cpp
#include "IRemoteControlProtocolModule.h"
#include "RemoteControlProtocol.h"
```

### 基本用法

**1. 获取协议模块并查询协议**

```cpp
// 来源：基于 IRemoteControlProtocolModule.h 接口推断
IRemoteControlProtocolModule& ProtocolModule = IRemoteControlProtocolModule::Get();

// 检查协议是否被禁用
if (!ProtocolModule.IsRCProtocolsDisable())
{
    // 获取所有已注册协议的名称
    TArray<FName> ProtocolNames = ProtocolModule.GetProtocolNames();
    
    // 获取特定协议
    TSharedPtr<IRemoteControlProtocol> DMXProtocol = ProtocolModule.GetProtocolByName(FName("DMX"));
    if (DMXProtocol.IsValid())
    {
        // 对协议进行操作...
    }
}
```

**2. 创建自定义协议（继承 FRemoteControlProtocol）**

```cpp
// 来源：基于 RemoteControlProtocol.h 基类推断
class FMyCustomProtocol : public FRemoteControlProtocol
{
public:
    FMyCustomProtocol() : FRemoteControlProtocol(FName("MyCustomProtocol"))
    {
    }

    // 实现初始化
    virtual void Init() override
    {
        // 初始化你的协议硬件或连接
    }

    // 创建协议实体，定义协议特有的数据结构
    virtual FRemoteControlProtocolEntityPtr CreateNewProtocolEntity(FProperty* InProperty, URemoteControlPreset* InOwner, FGuid InPropertyId) const override
    {
        // 返回一个包含你协议特有字段（如端口号、设备ID）的 TStructOnScope
        FRemoteControlProtocolEntityPtr Entity = MakeShared<TStructOnScope<FRemoteControlProtocolEntity>>();
        Entity->InitializeAs<FMyCustomProtocolEntity>(); // FMyCustomProtocolEntity 需要你定义
        // ... 填充默认值
        return Entity;
    }

    // 获取你协议实体的 UScriptStruct
    virtual UScriptStruct* GetProtocolScriptStruct() const override
    {
        return FMyCustomProtocolEntity::StaticStruct();
    }

    // 处理接收到的协议值
    virtual void QueueValue(const FRemoteControlProtocolEntityPtr InProtocolEntity, const double InProtocolValue) override
    {
        // 将外部值（如 0-1023）映射到属性范围，并加入队列
        double MappedValue = MapValueToRange(InProtocolValue, 0, 1023, 0.0, 1.0);
        FRemoteControlProtocol::QueueValue(InProtocolEntity, MappedValue);
    }

    // 在每帧开始时应用队列中的值
    virtual void OnBeginFrame() override
    {
        FRemoteControlProtocol::OnBeginFrame(); // 调用基类实现来应用值
        // 你可以在这里添加额外的每帧逻辑
    }

#if WITH_EDITOR
    // 注册在 Remote Control Panel 中显示的列
    virtual void RegisterColumns() override
    {
        REGISTER_COLUMN(“Port”, FText::FromString(“Port”), ProtocolColumnConstants::ColumnSizeSmall);
        REGISTER_COLUMN(“DeviceID”, FText::FromString(“Device ID”), ProtocolColumnConstants::ColumnSizeNormal);
    }
#endif
};
```

### 进阶用法

**注册自定义协议到模块**

```cpp
// 来源：基于 IRemoteControlProtocolModule.h 接口推断
// 通常在你的协议模块的 StartupModule 中调用
void FMyProtocolModule::StartupModule()
{
    IRemoteControlProtocolModule& ProtocolModule = IRemoteControlProtocolModule::Get();
    MyProtocol = MakeShared<FMyCustomProtocol>();
    ProtocolModule.AddProtocol(FName("MyCustomProtocol"), MyProtocol.ToSharedRef());
}

void FMyProtocolModule::ShutdownModule()
{
    if (MyProtocol.IsValid())
    {
        IRemoteControlProtocolModule& ProtocolModule = IRemoteControlProtocolModule::Get();
        ProtocolModule.RemoveProtocol(FName("MyCustomProtocol"), MyProtocol.ToSharedRef());
    }
}
```

**应用/卸载协议绑定**

```cpp
// 来源：基于 IRemoteControlProtocolModule.h 接口推断
// 当打开一个 Remote Control Preset 时
URemoteControlPreset* Preset = ...;
IRemoteControlProtocolModule::Get().ApplyProtocolBindings(Preset);

// 当关闭或销毁 Preset 时
IRemoteControlProtocolModule::Get().UnapplyProtocolBindings(Preset);
```

## Demo 示例

一个最小化的自定义协议实现框架。

**MyCustomProtocol.h**
```cpp
#pragma once
#include "RemoteControlProtocol.h"
#include "MyCustomProtocol.generated.h"

USTRUCT()
struct FMyCustomProtocolEntity : public FRemoteControlProtocolEntity
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category="Custom")
    int32 Port = 1;

    UPROPERTY(EditAnywhere, Category="Custom")
    FString DeviceID;
};

class FMyCustomProtocol : public FRemoteControlProtocol
{
public:
    FMyCustomProtocol();
    virtual ~FMyCustomProtocol() override;

    //~ Begin IRemoteControlProtocol interface
    virtual void Init() override;
    virtual FRemoteControlProtocolEntityPtr CreateNewProtocolEntity(FProperty* InProperty, URemoteControlPreset* InOwner, FGuid InPropertyId) const override;
    virtual UScriptStruct* GetProtocolScriptStruct() const override;
    virtual void QueueValue(const FRemoteControlProtocolEntityPtr InProtocolEntity, const double InProtocolValue) override;
    virtual void OnBeginFrame() override;
#if WITH_EDITOR
    virtual void RegisterColumns() override;
#endif
    //~ End IRemoteControlProtocol interface
};
```

**MyCustomProtocol.cpp**
```cpp
#include "MyCustomProtocol.h"
#include "RemoteControlPreset.h"

FMyCustomProtocol::FMyCustomProtocol()
    : FRemoteControlProtocol(FName("MyCustom"))
{
}

FMyCustomProtocol::~FMyCustomProtocol()
{
}

void FMyCustomProtocol::Init()
{
    // 初始化你的协议，例如打开串口或网络连接
}

FRemoteControlProtocolEntityPtr FMyCustomProtocol::CreateNewProtocolEntity(FProperty* InProperty, URemoteControlPreset* InOwner, FGuid InPropertyId) const
{
    FRemoteControlProtocolEntityPtr Entity = MakeShared<TStructOnScope<FRemoteControlProtocolEntity>>();
    Entity->InitializeAs<FMyCustomProtocolEntity>();
    // 可以在这里设置一些基于 InProperty 的默认值
    return Entity;
}

UScriptStruct* FMyCustomProtocol::GetProtocolScriptStruct() const
{
    return FMyCustomProtocolEntity::StaticStruct();
}

void FMyCustomProtocol::QueueValue(const FRemoteControlProtocolEntityPtr InProtocolEntity, const double InProtocolValue)
{
    // 简单示例：假设输入是 0-100 的百分比，直接映射到 0.0-1.0
    double MappedValue = FMath::Clamp(InProtocolValue / 100.0, 0.0, 1.0);
    FRemoteControlProtocol::QueueValue(InProtocolEntity, MappedValue);
}

void FMyCustomProtocol::OnBeginFrame()
{
    // 调用基类方法来实际应用队列中的值到绑定的属性
    FRemoteControlProtocol::OnBeginFrame();
}

#if WITH_EDITOR
void FMyCustomProtocol::RegisterColumns()
{
    REGISTER_COLUMN(“Port”, FText::FromString(“Port”), ProtocolColumnConstants::ColumnSizeSmall);
    REGISTER_COLUMN(“DeviceID”, FText::FromString(“Device ID”), ProtocolColumnConstants::ColumnSizeMedium);
}
#endif
```

## 模块依赖

从模块名称和常见实践推断，`RemoteControlProtocol` 模块很可能依赖以下模块。**注意：以下为基于模块命名和功能的合理推测，并非直接来自 Build.cs 文件。**

| 模块 | 用途 |
|---|---|
| `RemoteControlCommon` | 提供 Remote Control 系统共用的数据结构、工具函数和基础类型。 |
| `RemoteControlProtocolWidgets` | 提供协议在编辑器 UI（如 Remote Control Panel）中显示所需的 Slate 控件和列定义。 |

## 维护状态

### 近期更新

```
- e232a05a115e Remote Control: fixed issue where the protocols kept running even after the RC asset window was closed
- 150e4ced7d16 Remote Control: Protocol bindings no longer work after deleting a property or binding and undo the change
- e1b4328bc877 Remote Control: Fix issues when controlling struct properties with Remote Control Protocols, fix issues specific to controlling struct properties that support masking such as FVector or FColor
```

### 维护评价

-   **创建时间**：该插件创建于 2019 年，已有约 6 年历史，属于成熟组件。
-   **近期活动**：最近的提交集中在修复协议绑定相关的 Bug，表明该模块仍在被积极使用和维护，以解决实际生产中遇到的问题。
-   **维护状态**：**维护中**。虽然没有看到重大的新功能提交，但持续的 Bug 修复证明其处于活跃维护状态，是虚拟制片工作流中的关键组件。
-   **推荐使用**：**推荐**。对于需要在虚拟制片、现场活动或自动化流程中集成外部控制协议的项目，此模块是官方提供的标准且强大的解决方案。其架构清晰，扩展性好。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/remote-control-api-in-unreal-engine/) (Remote Control API 总体文档)