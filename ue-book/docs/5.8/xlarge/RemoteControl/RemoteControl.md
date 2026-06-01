```markdown
# Remote Control API

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制 API |
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControl` (Runtime), `RemoteControlCommon` (Runtime), `RemoteControlLogic` (Runtime), `RemoteControlMultiUser` (Runtime), `RemoteControlProtocol` (Runtime), `RemoteControlProtocolWidgets` (Runtime), `RemoteControlUI` (Runtime), `WebRemoteControl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl) | |

## 用途

Remote Control API 是 UE 中最强大的远程操控系统。它的核心目标是：**让外部应用能够通过网络（HTTP / WebSocket）读取和写入引擎中的任意 UObject 属性、调用函数、操控 Actor，而无需在引擎内部编写任何 C++ 代码。**

这个 plugin 解决的关键问题：

1. **虚制作（Virtual Production）流水线集成**：在片场，灯光师可以通过 iPad 或自定义 Web 界面实时调整引擎中的灯光参数、材质颜色、摄像机位置
2. **外部控制软件对接**：通过 WebSocket 或 HTTP 让 TouchDesigner、Qlab、DMX 控制台等第三方软件直接控制引擎
3. **Preset 机制**：将需要远程控制的属性/函数组织成 Preset（预设），每个 Preset 可以包含任意数量的暴露属性、暴露函数和暴露 Actor
4. **协议绑定**：支持将外部协议（DMX、OSC、MIDI 等）的输入值映射到引擎属性上，实现自动化控制
5. **虚拟属性（Virtual Property）**：提供不直接绑定 UObject 的控制器，可以作为中间变量或独立参数使用

## 使用场景

- 你在做虚拟制片（VP），片场灯光师需要实时调整场景灯光的亮度和颜色 → 用 Remote Control API 暴露灯光属性到 Preset，通过 Web 界面控制
- 你在做现场直播，需要外部软件实时切换摄像机角度和材质效果 → 用 WebSocket 连接 Remote Control API 实现毫秒级响应
- 你需要让 DMX 控制台直接控制引擎中的灯光和特效 → 用 Protocol Binding 将 DMX 通道映射到 UE 属性
- 你在开发主题公园的互动装置，需要通过 PLC 或其他硬件控制引擎内容 → 用 HTTP API 读写属性和调用函数
- 你需要在运行时通过蓝图暴露某些属性给外部系统 → 用 `URemoteControlFunctionLibrary` 的 `ExposeProperty` / `ExposeFunction` 节点
- 你需要批量将某类 Actor 的特定属性暴露到远程控制 → 用 Signature 系统定义模板后一键应用

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExposeProperty` | 在指定 Preset 中暴露一个对象的属性 | `URemoteControlFunctionLibrary` |
| `ExposeFunction` | 在指定 Preset 中暴露一个对象的函数 | `URemoteControlFunctionLibrary` |
| `ExposeActor` | 在指定 Preset 中暴露一个 Actor | `URemoteControlFunctionLibrary` |
| `ApplyColorWheelDelta` | 基于色轮坐标对 FLinearColor 属性施加增量修改 | `URemoteControlFunctionLibrary` |
| `ApplyColorGradingWheelDelta` | 基于色轮坐标对 FVector4 (RGBV) 属性施加增量修改 | `URemoteControlFunctionLibrary` |
| `GetValueBool` | 从虚拟属性中获取 Bool 值 | `URCVirtualPropertyBase` |
| `GetValueFloat` | 从虚拟属性中获取 Float 值 | `URCVirtualPropertyBase` |
| `GetValueInt32` | 从虚拟属性中获取 Int32 值 | `URCVirtualPropertyBase` |
| `GetValueString` | 从虚拟属性中获取 String 值 | `URCVirtualPropertyBase` |
| `GetValueVector` | 从虚拟属性中获取 FVector 值 | `URCVirtualPropertyBase` |
| `GetValueLinearColor` | 从虚拟属性中获取 FLinearColor 值 | `URCVirtualPropertyBase` |
| `SetValueBool` | 设置虚拟属性的 Bool 值 | `URCVirtualPropertyBase` |
| `SetValueFloat` | 设置虚拟属性的 Float 值 | `URCVirtualPropertyBase` |
| `SetValueInt32` | 设置虚拟属性的 Int32 值 | `URCVirtualPropertyBase` |
| `SetValueString` | 设置虚拟属性的 String 值 | `URCVirtualPropertyBase` |
| `SetValueVector` | 设置虚拟属性的 FVector 值 | `URCVirtualPropertyBase` |
| `SetValueLinearColor` | 设置虚拟属性的 FLinearColor 值 | `URCVirtualPropertyBase` |
| `GetDisplayValueAsString` | 获取虚拟属性值的可读字符串表示 | `URCVirtualPropertyBase` |

### 使用示例（蓝图描述）

**示例 1：运行时暴露 Actor 属性**

1. 在你的 Actor 蓝图中，使用 `ExposeActor` 节点将自身暴露到一个 Remote Control Preset
2. 指定一个已创建的 `URemoteControlPreset` 资产
3. 设置 `FRemoteControlOptionalExposeArgs` 中的 `DisplayName` 和 `GroupName`（可选）
4. 暴露后，外部可通过 HTTP GET `/remote/presets` 查询到该 Preset

**示例 2：运行时暴露单个属性**

1. 使用 `ExposeProperty` 节点
2. 传入 Preset、源对象和属性路径字符串（如 `"RelativeLocation"` 或 `"MyStructProperty.NestedValue"`）
3. 属性被暴露后可通过 WebSocket 或 HTTP 修改

**示例 3：使用虚拟属性作为控制器**

1. 获取 Preset 的控制器容器
2. 调用 `AddProperty` 添加一个虚拟属性
3. 通过 `SetValueFloat` / `GetValueFloat` 等读写虚拟属性值
4. 虚拟属性可以绑定到实体属性，实现值变化时自动同步

## C++ 用法

### 头文件引入

```cpp
#include "IRemoteControlModule.h"
#include "RemoteControlPreset.h"
#include "RemoteControlField.h"
#include "RemoteControlBinding.h"
#include "RemoteControlFunctionLibrary.h"
#include "RCVirtualProperty.h"
#include "RCVirtualPropertyContainer.h"
#include "RemoteControlPropertyIdRegistry.h"
```

### 基本用法

**获取模块接口并解析/读写属性**：

```cpp
// 来源: Public/IRemoteControlModule.h
// 获取远程控制模块单例
IRemoteControlModule& RCModule = IRemoteControlModule::Get();

// 解析一个对象引用（读写访问）
FRCObjectReference ObjectRef;
FString ErrorText;
bool bSuccess = RCModule.ResolveObject(
    ERCAccess::WRITE_ACCESS,
    TEXT("/Game/Maps/MyLevel.MyLevel:PersistentLevel.MyActor_0"),
    TEXT("RelativeLocation"),
    ObjectRef,
    &ErrorText
);

if (bSuccess)
{
    // 序列化读取属性值
    // 使用 IStructSerializerBackend 进行序列化...
    
    // 设置属性值
    // 使用 IStructDeserializerBackend 反序列化数据并写入...
    RCModule.SetObjectProperties(
        ObjectRef,
        DeserializerBackend,
        ERCPayloadType::Json,
        InPayload,
        ERCModifyOperation::EQUAL
    );
}
```

**解析并调用函数**：

```cpp
// 来源: Public/IRemoteControlModule.h
// 解析远程函数调用
FRCCallReference CallRef;
bool bResolved = RCModule.ResolveCall(
    TEXT("/Game/Maps/MyLevel.MyLevel:PersistentLevel.MyActor_0"),
    TEXT("MyBlueprintFunction"),
    CallRef,
    &ErrorText
);

if (bResolved)
{
    FRCCall Call;
    Call.CallRef = CallRef;
    // 设置函数参数（通过 ParamStruct 或 ParamData）
    
    RCModule.InvokeCall(Call, ERCPayloadType::Json);
}
```

**注册/查询 Preset**：

```cpp
// 来源: Public/IRemoteControlModule.h
// 注册嵌入式 Preset
URemoteControlPreset* MyPreset = NewObject<URemoteControlPreset>();
RCModule.RegisterEmbeddedPreset(MyPreset, false);

// 通过名称查询 Preset
URemoteControlPreset* Found = RCModule.ResolvePreset(FName("MyPreset"));

// 获取所有 Preset 资产
TArray<FAssetData> PresetAssets;
RCModule.GetPresetAssets(PresetAssets, true);

// 用完后销毁嵌入式 Preset
RCModule.UnregisterEmbeddedPreset(MyPreset);
```

### 进阶用法

**暴露属性/函数到 Preset（运行时）**：

```cpp
// 来源: Public/RemoteControlFunctionLibrary.h + Public/RemoteControlPreset.h
#include "RemoteControlFunctionLibrary.h"

// 创建 Preset
URemoteControlPreset* Preset = NewObject<URemoteControlPreset>();

// 暴露一个 Actor
FRemoteControlOptionalExposeArgs ActorArgs;
ActorArgs.DisplayName = TEXT("MyActor");
ActorArgs.GroupName = TEXT("Lights");
URemoteControlFunctionLibrary::ExposeActor(Preset, MyActor, ActorArgs);

// 暴露一个属性
FRemoteControlOptionalExposeArgs PropArgs;
PropArgs.DisplayName = TEXT("Intensity");
URemoteControlFunctionLibrary::ExposeProperty(Preset, MyLight, TEXT("Intensity"), PropArgs);

// 暴露一个函数
FRemoteControlOptionalExposeArgs FuncArgs;
URemoteControlFunctionLibrary::ExposeFunction(Preset, MyActor, TEXT("MyFunction"), FuncArgs);
```

**使用属性句柄读写属性值**：

```cpp
// 来源: Public/IRemoteControlPropertyHandle.h + Public/RemoteControlField.h
// 获取远程控制属性句柄
TSharedPtr<IRemoteControlPropertyHandle> Handle = 
    IRemoteControlPropertyHandle::GetPropertyHandle(FName("MyPreset"), PropertyId);

if (Handle.IsValid())
{
    // 读取 float 值
    float Value;
    if (Handle->GetValue(Value))
    {
        UE_LOG(LogTemp, Log, TEXT("Value: %f"), Value);
    }
    
    // 写入 float 值
    Handle->SetGenerateTransaction(true); // 产生事务记录
    Handle->SetValue(42.0f);
    
    // 获取子属性句柄（用于结构体内部成员）
    TSharedPtr<IRemoteControlPropertyHandle> ChildHandle = 
        Handle->GetChildHandle(FName("X"));
    
    // 按路径获取深层属性
    TSharedPtr<IRemoteControlPropertyHandle> DeepHandle = 
        Handle->GetChildHandleByFieldPath(TEXT("MyStruct.NestedArray[0].Value"));
}
```

**协议实体处理（将协议输入映射到属性）**：

```cpp
// 来源: Public/RemoteControlProtocolEntityProcessor.h
#include "RemoteControlProtocolEntityProcessor.h"

// 处理一组协议实体映射
TMap<TSharedPtr<TStructOnScope<FRemoteControlProtocolEntity>>, double> EntityToValueMap;
// 填充映射...

UE::RemoteControl::ProtocolEntityProcessor::ProcessEntities(EntityToValueMap);
```

**使用 PropertyId 系统做属性联动**：

```cpp
// 来源: Public/RemoteControlPropertyIdRegistry.h
// PropertyId 系统允许将多个属性绑定到同一个 ID，
// 当一个属性变化时，自动更新所有同 ID 的属性

// 获取 Preset 的 PropertyId 注册表
URemoteControlPropertyIdRegistry* IdRegistry = Preset->GetPropertyIdRegistry();

// 获取某个 PropertyId 关联的所有 EntityId
TSet<FGuid> EntityIds = IdRegistry->GetEntityIdsForPropertyId(FName("MyPropertyId"));

// 执行链式反应 - 当某个属性变化时，同步更新所有关联属性
FRemoteControlPropertyIdArgs Args;
IdRegistry->PerformChainReaction(Args);
```

## Demo 示例

**最小示例：运行时创建 Preset 并暴露属性**

```cpp
// MyRemoteControlComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "IRemoteControlModule.h"
#include "RemoteControlPreset.h"
#include "RemoteControlFunctionLibrary.h"
#include "MyRemoteControlComponent.generated.h"

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class MYGAME_API UMyRemoteControlComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category = "Remote Control")
    FString PresetName = TEXT("GameControl");

    UPROPERTY()
    TObjectPtr<URemoteControlPreset> RuntimePreset;

    /** 暴露指定 Actor 的属性到远程控制 */
    UFUNCTION(BlueprintCallable, Category = "Remote Control")
    bool ExposeObjectProperty(UObject* TargetObject, const FString& PropertyPath, const FString& DisplayName);

    /** 通过 PropertyHandle 读取已暴露的属性值 */
    UFUNCTION(BlueprintCallable, Category = "Remote Control")
    float GetExposedFloatValue(FGuid PropertyId);

    /** 通过 PropertyHandle 设置已暴露的属性值 */
    UFUNCTION(BlueprintCallable, Category = "Remote Control")
    bool SetExposedFloatValue(FGuid PropertyId, float NewValue);
};
```

```cpp
// MyRemoteControlComponent.cpp
#include "MyRemoteControlComponent.h"
#include "IRemoteControlPropertyHandle.h"

void UMyRemoteControlComponent::BeginPlay()
{
    Super::BeginPlay();

    IRemoteControlModule& RCModule = IRemoteControlModule::Get();

    // 创建一个运行时 Preset
    RuntimePreset = RCModule.CreateTransientPreset();
    if (RuntimePreset)
    {
        // 注册嵌入式 Preset 使其可通过网络访问
        RCModule.RegisterEmbeddedPreset(RuntimePreset);
        
        // 监听错误
        RCModule.OnError().AddLambda([](const FString& Msg, ELogVerbosity::Type Verbosity)
        {
            UE_LOG(LogTemp, Warning, TEXT("[RemoteControl] %s"), *Msg);
        });
    }
}

void UMyRemoteControlComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (RuntimePreset)
    {
        IRemoteControlModule& RCModule = IRemoteControlModule::Get();
        RCModule.UnregisterEmbeddedPreset(RuntimePreset);
        RCModule.DestroyTransientPreset(RuntimePreset->GetName());
        RuntimePreset = nullptr;
    }

    Super::EndPlay(EndPlayReason);
}

bool UMyRemoteControlComponent::ExposeObjectProperty(UObject* TargetObject, const FString& PropertyPath, const FString& DisplayName)
{
    if (!RuntimePreset || !TargetObject)
    {
        return false;
    }

    FRemoteControlOptionalExposeArgs Args;
    Args.DisplayName = DisplayName;

    return URemoteControlFunctionLibrary::ExposeProperty(
        RuntimePreset, TargetObject, PropertyPath, Args
    );
}

float UMyRemoteControlComponent::GetExposedFloatValue(FGuid PropertyId)
{
    if (!RuntimePreset)
    {
        return 0.f;
    }

    TSharedPtr<IRemoteControlPropertyHandle> Handle =
        IRemoteControlPropertyHandle::GetPropertyHandle(RuntimePreset->GetName(), PropertyId);

    float Value = 0.f;
    if (Handle.IsValid())
    {
        Handle->GetValue(Value);
    }
    return Value;
}

bool UMyRemoteControlComponent::SetExposedFloatValue(FGuid PropertyId, float NewValue)
{
    if (!RuntimePreset)
    {
        return false;
    }

    TSharedPtr<IRemoteControlPropertyHandle> Handle =
        IRemoteControlPropertyHandle::GetPropertyHandle(RuntimePreset->GetName(), PropertyId);

    if (Handle.IsValid())
    {
        Handle->SetGenerateTransaction(true);
        return Handle->SetValue(NewValue);
    }
    return false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StructUtils` | 结构体工具（FStructOnScope、TInstancedStruct 等） |
| `PropertyBag` | 属性包（FInstancedPropertyBag），用于虚拟属性的动态类型存储 |
| `Json` | JSON 序列化/反序列化 |
| `JsonUtilities` | JSON 到 UObject 属性的转换工具 |
| `Serialization` | 结构体序列化框架（IStructSerializerBackend） |
| `WebSockets` | WebSocket 通信支持 |
| `HTTP` | HTTP 服务器/客户端支持 |
| `MessagingCommon` | 消息总线通用功能 |
| `Messenger` | 消息传递系统 |
| `InterceptionCore` | 远程控制拦截框架核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1716f2e0` | Remote Control: added missing ApplyColorWheelDelta and ApplyColorGradingWheelDelta to the built-in a | 补充了色轮增量修改节点到内置动作列表中 |
| 2026-05-20 | `d724bb52` | Remote Control: fixed uninitialized ObjectClass in FRCRemoteFunctionCallParams, sometimes causing a | 修复了远程函数调用参数中 ObjectClass 未初始化导致的随机崩溃 |
| 2026-05-20 | `12d5ae7f` | Remote Control: added allow list for remote function calls, and specifying built-in functions to all | 新增远程函数调用白名单机制，并将内置函数加入允许列表 |
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 相关面板移至独立分组（间接关联） |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double→float 截断警告 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- **创建于 2019 年**，是 Epic 虚拟制片工具链的核心组件之一
- **持续活跃开发**：2026 年 5 月仍有功能性更新（色轮支持、函数调用白名单、bug 修复）
- 经历了多次重大架构迭代：从 4.26 的 ComponentChain → Bindings 系统 → Entity/Field 分离 → Protocol Binding 系统 → 拦截框架
- 代码中大量 `UE_DEPRECATED` 标记说明 API 在不断演进，旧接口有完善的迁移路径
- **8 个模块**的庞大架构体现了其作为基础设施级插件的定位
- **已知限制**：Map 键目前仅支持字符串类型索引；Masking 系统在 5.5 已标记为自动处理
- **强烈推荐使用**：任何需要外部系统控制引擎的场景都应该考虑此插件，HTTP/WebSocket API 开箱即用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-api-for-unreal-engine)
```