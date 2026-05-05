# Remote Control API

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControl` (Runtime), `RemoteControlCommon` (Runtime), `RemoteControlLogic` (Runtime), `RemoteControlMultiUser` (Runtime), `RemoteControlProtocol` (Runtime), `RemoteControlProtocolWidgets` (Runtime), `RemoteControlUI` (Runtime), `WebRemoteControl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl) | |

---

## 用途

Remote Control API 是一套完整的远程控制框架，允许外部应用程序通过 **HTTP REST API** 或 **WebSocket** 实时操控 Unreal Engine。它解决的核心问题是：**如何让第三方工具（Web 应用、平板控制面、自动化脚本等）与 UE 引擎进行双向通信**。

该插件的核心架构围绕以下概念构建：

- **Preset（预设）**：远程控制的配置单元，包含所有暴露的实体（属性、函数、Actor）
- **Entity（实体）**：被暴露到远程控制面板的对象，可以是属性（Property）、函数（Function）或 Actor
- **Binding（绑定）**：实体与实际 UObject 之间的桥梁，支持运行时重新绑定（Rebinding）
- **Protocol（协议）**：通信协议抽象层，支持自定义协议扩展
- **Signature（签名）**：批量暴露属性的模板系统，可快速将一组预定义属性暴露到 Preset
- **Virtual Property（虚拟属性）**：不依赖现有 UProperty 的动态属性，使用 PropertyBag 实现

与简单的 HTTP 推送不同，Remote Control API 提供了完整的属性读写、函数调用、值映射（Mapping）、遮罩（Masking）、事务支持（Transaction）和多用户同步能力。

---

## 使用场景

- **虚拟制片（Virtual Production）**：导演在 iPad 上通过 Web 界面实时调整灯光、摄像机参数、后期效果
- **现场演出控制**：通过自定义控制面（OSC/MIDI 等协议）驱动 UE 中的视觉效果
- **自动化测试与 CI/CD**：通过 HTTP API 自动化测试游戏逻辑、截图、性能基准
- **多用户协作**：多个操作员同时控制不同方面的场景参数
- **Web 仪表盘**：构建基于浏览器的实时监控和控制面板
- **第三方 DCC 工具集成**：从 Maya、Blender 等工具直接控制 UE 中的资产属性
- **自定义协议集成**：通过 Protocol 扩展接入 OSC、MIDI、DMX 等工业协议

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Expose Property` | 将对象的属性暴露到远程控制预设中 | `URemoteControlFunctionLibrary` |
| `Expose Function` | 将对象的函数暴露到远程控制预设中 | `URemoteControlFunctionLibrary` |
| `Expose Actor` | 将整个 Actor 暴露到远程控制预设中 | `URemoteControlFunctionLibrary` |
| `Get Label` | 获取暴露实体的标签名 | `FRemoteControlEntity` |
| `Get Id` | 获取暴露实体的唯一标识 | `FRemoteControlEntity` |
| `Get Bound Object` | 获取实体绑定的实际对象 | `FRemoteControlEntity` |
| `Bind Object` | 将实体重新绑定到另一个对象 | `FRemoteControlEntity` |
| `Set Metadata Value` | 设置实体的元数据键值对 | `FRemoteControlEntity` |
| `Get Metadata` | 获取实体的所有元数据 | `FRemoteControlEntity` |
| `Get Property Handle` | 通过预设名和属性标签获取类型安全的属性句柄 | `IRemoteControlPropertyHandle` (Static) |

### 使用示例

**场景：将一个 Actor 的位置属性暴露到远程控制**

1. 在场景中放置一个 `ARemoteControlPresetActor`，它会自动关联一个 `URemoteControlPreset`
2. 从 Preset Actor 获取 Preset 引用
3. 调用 `Expose Property` 节点：
   - **Preset**：连接到 Preset Actor 的 `Preset` 属性
   - **Source Object**：连接到目标 Actor
   - **Property**：输入 `"ActorLocation"` 或 `"RootComponent.RelativeLocation"`
   - **Args**：可选设置 `DisplayName` 和 `GroupName`
4. 暴露成功后，可通过 HTTP/WebSocket 访问该属性

**场景：通过属性句柄读写值**

1. 调用 `Get Property Handle`（静态节点），传入预设名称和属性标签
2. 使用返回的 Handle 调用 `Get Value` / `Set Value` 系列节点
3. 支持的类型包括：Float、Bool、Int、String、Vector、Rotator、Color、LinearColor 等

---

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "IRemoteControlModule.h"
#include "RemoteControlPreset.h"
#include "RemoteControlField.h"
#include "RemoteControlEntity.h"

// 属性句柄（类型安全读写）
#include "IRemoteControlPropertyHandle.h"

// 签名系统（批量暴露）
#include "RCSignature.h"
#include "RCSignatureRegistry.h"

// 虚拟属性
#include "RCVirtualProperty.h"
#include "RCVirtualPropertyContainer.h"

// 蓝图函数库
#include "RemoteControlFunctionLibrary.h"

// 绑定系统
#include "RemoteControlBinding.h"

// 协议绑定
#include "RemoteControlProtocolBinding.h"
```

### 基本用法

**获取模块实例并暴露属性**

```cpp
// 获取 Remote Control 模块
IRemoteControlModule& RCModule = IRemoteControlModule::Get();

// 假设已有一个 URemoteControlPreset* Preset
// 暴露一个属性
FRemoteControlPresetExposeArgs Args;
Args.Label = TEXT("LightIntensity");
Args.GroupName = TEXT("Lighting");

bool bSuccess = Preset->ExposeProperty(
    MyLightActor,
    FRCFieldPathInfo(TEXT("PointLightComponent.Intensity")),
    Args
);

// 暴露一个函数
FRemoteControlPresetExposeArgs FuncArgs;
FuncArgs.Label = TEXT("ToggleLight");
Preset->ExposeFunction(MyLightActor, TEXT("ToggleLightFunction"), FuncArgs);

// 暴露一个 Actor
FRemoteControlPresetExposeArgs ActorArgs;
ActorArgs.Label = TEXT("MainLight");
Preset->ExposeActor(MyLightActor, ActorArgs);
```

**使用属性句柄进行类型安全读写**

```cpp
#include "IRemoteControlPropertyHandle.h"

// 通过预设名和属性 ID 获取句柄
TSharedPtr<IRemoteControlPropertyHandle> Handle =
    IRemoteControlPropertyHandle::GetPropertyHandle(
        Preset->GetFName(),
        PropertyId  // FGuid
    );

if (Handle.IsValid())
{
    // 读取浮点值
    float Intensity = 0.0f;
    if (Handle->GetValue(Intensity))
    {
        UE_LOG(LogTemp, Log, TEXT("Intensity: %f"), Intensity);
    }

    // 写入浮点值
    Handle->SetValue(5000.0f);

    // 读取向量值
    FVector Location;
    if (Handle->GetValue(Location))
    {
        UE_LOG(LogTemp, Log, TEXT("Location: %s"), *Location.ToString());
    }

    // 读取颜色值
    FLinearColor Color;
    if (Handle->GetValue(Color))
    {
        UE_LOG(LogTemp, Log, TEXT("Color: %s"), *Color.ToString());
    }
}
```

**遍历 Preset 中的所有暴露实体**

```cpp
// 获取所有暴露的实体
TArray<TSharedRef<FRemoteControlEntity>> Entities = Preset->GetExposedEntities();

for (const TSharedRef<FRemoteControlEntity>& Entity : Entities)
{
    FName Label = Entity->GetLabel();
    FGuid Id = Entity->GetId();
    
    // 获取绑定的对象
    UObject* BoundObject = Entity->GetBoundObject();
    if (BoundObject)
    {
        UE_LOG(LogTemp, Log, TEXT("Entity '%s' bound to: %s"),
            *Label.ToString(), *BoundObject->GetName());
    }

    // 检查实体类型
    if (Entity->GetStruct() == FRemoteControlField::StaticStruct())
    {
        const FRemoteControlField& Field = static_cast<const FRemoteControlField&>(Entity.Get());
        if (Field.FieldType == EExposedFieldType::Property)
        {
            UE_LOG(LogTemp, Log, TEXT("  -> Property: %s"), *Field.FieldName.ToString());
        }
        else if (Field.FieldType == EExposedFieldType::Function)
        {
            UE_LOG(LogTemp, Log, TEXT("  -> Function: %s"), *Field.FieldName.ToString());
        }
    }
}
```

### 进阶用法

**使用签名（Signature）批量暴露属性**

```cpp
#include "RCSignature.h"
#include "RCSignatureRegistry.h"

// 获取签名注册表（通常从 Preset 获取）
URCSignatureRegistry* SignatureRegistry = Preset->GetSignatureRegistry();

// 创建新签名
FRCSignature& Signature = SignatureRegistry->AddSignature();
Signature.DisplayName = FText::FromString(TEXT("BasicLightSetup"));
Signature.bEnabled = true;

// 添加字段到签名
FRCSignatureField Field = FRCSignatureField::CreateField(
    FRCFieldPathInfo(TEXT("Intensity")),
    MyLightActor,
    IntensityProperty  // const FProperty*
);
Signature.AddFields({Field});

// 将签名应用到一组对象
TArray<TWeakObjectPtr<UObject>> Objects;
Objects.Add(MyLightActor);
int32 AffectedCount = Signature.ApplySignature(Preset, Objects);
UE_LOG(LogTemp, Log, TEXT("Signature applied, %d properties affected"), AffectedCount);
```

**使用虚拟属性（Virtual Property）**

```cpp
#include "RCVirtualProperty.h"
#include "RCVirtualPropertyContainer.h"

// 获取 Preset 的虚拟属性容器
URCVirtualPropertyContainerBase* Container = Preset->GetVirtualPropertyContainer();

// 添加一个浮点虚拟属性
URCVirtualPropertyInContainer* VirtProp = Container->AddProperty(
    FName("CustomBrightness"),
    URCVirtualPropertyInContainer::StaticClass(),
    EPropertyBagPropertyType::Float
);

// 添加一个带元数据的属性（用于 Slate 控件的 Delta、Sensitivity 等）
TArray<FPropertyBagPropertyDescMetaData> MetaData;
MetaData.Add(FPropertyBagPropertyDescMetaData(
    FName("Delta"), TEXT("0.1")
));
URCVirtualPropertyInContainer* VirtPropWithMeta = Container->AddProperty(
    FName("FineControl"),
    URCVirtualPropertyInContainer::StaticClass(),
    EPropertyBagPropertyType::Float,
    nullptr,
    MetaData
);
```

**自定义属性工厂（Property Factory）**

```cpp
#include "RemoteControlEntityFactory.h"

class FMyCustomPropertyFactory : public IRemoteControlPropertyFactory
{
public:
    virtual TSharedPtr<FRemoteControlProperty> CreateRemoteControlProperty(
        URemoteControlPreset* Preset,
        UObject* Object,
        FRCFieldPathInfo FieldPath,
        FRemoteControlPresetExposeArgs Args) override
    {
        // 自定义属性创建逻辑
        // ...
        return nullptr;
    }

    virtual bool SupportExposedClass(UClass* Class) const override
    {
        // 声明支持的类
        return Class->IsChildOf(UMyCustomClass::StaticClass());
    }

    virtual void PostSetObjectProperties(UObject* Object, bool bInSuccess) const override
    {
        // 属性设置后的回调
        if (bInSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Custom property set successfully on %s"),
                *Object->GetName());
        }
    }
};

// 注册工厂
IRemoteControlModule& RCModule = IRemoteControlModule::Get();
// 通过模块接口注册自定义工厂
```

**使用协议绑定（Protocol Binding）进行值映射**

```cpp
#include "RemoteControlProtocolBinding.h"

// 协议绑定允许将外部协议的值范围映射到属性值范围
// 例如：将 MIDI 0-127 映射到灯光强度 0-10000

FRemoteControlProtocolMapping Mapping(Property, RangeValueSize);
// 设置映射范围值
// Mapping.SetRangeValue<float>(MinValue);
// Mapping.SetRangeValue<float>(MaxValue, 1);  // Max index
```

**修改操作标志（Modify Operation Flags）**

```cpp
#include "RCModifyOperationFlags.h"

// 控制属性修改时的行为
ERCModifyOperationFlags Flags = ERCModifyOperationFlags::None;

// 跳过属性变更事件（不触发 PropertyChanged）
Flags |= ERCModifyOperationFlags::SkipPropertyChangeEvents;

// 跳过事务（不支持撤销/重做）
Flags |= ERCModifyOperationFlags::SkipTransactions;
```

---

## Demo 示例

以下示例展示如何创建一个自定义 Actor，通过 C++ 代码将自身属性暴露到 Remote Control Preset，并通过属性句柄进行读写。

### MyRemoteControlledActor.h

```cpp
// MyRemoteControlledActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyRemoteControlledActor.generated.h"

class URemoteControlPreset;
class IRemoteControlPropertyHandle;

UCLASS()
class AMyRemoteControlledActor : public AActor
{
    GENERATED_BODY()

public:
    AMyRemoteControlledActor();

    virtual void BeginPlay() override;

    /** 暴露属性到指定的 Remote Control Preset */
    UFUNCTION(BlueprintCallable, Category = "Remote Control")
    void ExposeToRemoteControl(URemoteControlPreset* InPreset);

    /** 通过 Remote Control 更新亮度 */
    UFUNCTION(BlueprintCallable, Category = "Remote Control")
    void UpdateBrightnessRemotely(float NewBrightness);

    /** 通过 Remote Control 读取当前亮度 */
    UFUNCTION(BlueprintCallable, Category = "Remote Control")
    float ReadBrightnessRemotely() const;

public:
    /** 可远程控制的亮度值 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lighting")
    float Brightness = 1.0f;

    /** 可远程控制的颜色 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lighting")
    FLinearColor LightColor = FLinearColor::White;

    /** 可远程控制的是否启用 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lighting")
    bool bIsEnabled = true;

private:
    /** 关联的 Preset 名称 */
    FName AssociatedPresetName;

    /** 属性 ID，用于后续通过句柄访问 */
    FGuid BrightnessPropertyId;
};
```

### MyRemoteControlledActor.cpp

```cpp
// MyRemoteControlledActor.cpp
#include "MyRemoteControlledActor.h"

#include "RemoteControlPreset.h"
#include "RemoteControlField.h"
#include "RemoteControlFunctionLibrary.h"
#include "IRemoteControlPropertyHandle.h"

AMyRemoteControlledActor::AMyRemoteControlledActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyRemoteControlledActor::BeginPlay()
{
    Super::BeginPlay();
}

void AMyRemoteControlledActor::ExposeToRemoteControl(URemoteControlPreset* InPreset)
{
    if (!InPreset)
    {
        UE_LOG(LogTemp, Warning, TEXT("AMyRemoteControlledActor: Invalid Preset"));
        return;
    }

    AssociatedPresetName = InPreset->GetFName();

    // 暴露亮度属性
    FRemoteControlPresetExposeArgs BrightnessArgs;
    BrightnessArgs.Label = TEXT("ActorBrightness");
    BrightnessArgs.GroupName = TEXT("MyActorControls");
    bool bSuccess = InPreset->ExposeProperty(
        this,
        FRCFieldPathInfo(TEXT("Brightness")),
        BrightnessArgs
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Exposed Brightness successfully"));
    }

    // 暴露颜色属性
    FRemoteControlPresetExposeArgs ColorArgs;
    ColorArgs.Label = TEXT("ActorColor");
    ColorArgs.GroupName = TEXT("MyActorControls");
    InPreset->ExposeProperty(
        this,
        FRCFieldPathInfo(TEXT("LightColor")),
        ColorArgs
    );

    // 暴露启用状态属性
    FRemoteControlPresetExposeArgs EnabledArgs;
    EnabledArgs.Label = TEXT("ActorEnabled");
    EnabledArgs.GroupName = TEXT("MyActorControls");
    InPreset->ExposeProperty(
        this,
        FRCFieldPathInfo(TEXT("bIsEnabled")),
        EnabledArgs
    );

    UE_LOG(LogTemp, Log, TEXT("All properties exposed to Remote Control Preset: %s"),
        *InPreset->GetName());
}

void AMyRemoteControlledActor::UpdateBrightnessRemotely(float NewBrightness)
{
    if (AssociatedPresetName.IsNone())
    {
        UE_LOG(LogTemp, Warning, TEXT("Actor not exposed to any Preset"));
        return;
    }

    // 通过属性句柄写入值
    TSharedPtr<IRemoteControlPropertyHandle> Handle =
        IRemoteControlPropertyHandle::GetPropertyHandle(
            AssociatedPresetName,
            FName("ActorBrightness")
        );

    if (Handle.IsValid())
    {
        Handle->SetValue(NewBrightness);
        UE_LOG(LogTemp, Log, TEXT("Brightness updated to %f via Remote Control"), NewBrightness);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Could not get property handle for Brightness"));
    }
}

float AMyRemoteControlledActor::ReadBrightnessRemotely() const
{
    if (AssociatedPresetName.IsNone())
    {
        return -1.0f;
    }

    TSharedPtr<IRemoteControlPropertyHandle> Handle =
        IRemoteControlPropertyHandle::GetPropertyHandle(
            AssociatedPresetName,
            FName("ActorBrightness")
        );

    if (Handle.IsValid())
    {
        float Value = 0.0f;
        if (Handle->GetValue(Value))
        {
            return Value;
        }
    }

    return -1.0f;
}
```

---

## 模块依赖

该插件包含 8 个模块，以下是各模块的职责说明：

| 模块 | 职责 |
|---|---|
| `RemoteControl` | 核心模块：实体（Entity）、绑定（Binding）、预设（Preset）、签名（Signature）、虚拟属性（Virtual Property） |
| `RemoteControlCommon` | 公共类型定义和工具函数，被其他所有模块依赖 |
| `RemoteControlLogic` | 远程控制的业务逻辑层，处理属性读写、函数调用等核心操作 |
| `RemoteControlMultiUser` | 多用户/多会话支持，处理多客户端并发控制的同步问题 |
| `RemoteControlProtocol` | 协议抽象层，定义协议实体和处理器接口，支持自定义协议扩展 |
| `RemoteControlProtocolWidgets` | 协议配置的 Slate UI 控件，用于编辑器中配置协议映射 |
| `RemoteControlUI` | Remote Control Panel 编辑器面板 UI |
| `WebRemoteControl` | HTTP/WebSocket 服务器实现，处理 REST API 和 WebSocket 连接 |

**使用者需要依赖的模块**（非标准依赖）：

| 模块 | 用途 |
|---|---|
| `StructUtils` | PropertyBag 和 InstancedStruct，用于虚拟属性和签名系统 |
| `RemoteControl` | 核心 API（实体、预设、属性句柄等） |
| `RemoteControlCommon` | 公共类型（如 `ERCMask`、`ERCAccess` 等枚举） |
| `WebRemoteControl` | 如果需要直接使用 HTTP/WebSocket 服务器 API |
| `RemoteControlProtocol` | 如果需要实现自定义协议扩展 |

---

## 维护状态

### 近期更新

```
- 17325108bde9 Remote Control: Protocol OverrideMasks is now (actually) saved when saved.
- ce6ff392ddca Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue for FTSTicker::RemoveTicker usage.
- 66c97e388bc2 [Remote Control] Adding a command to enable remote control interception local forwarding to make it easier to test.
```

### 维护评价

**综合评价：活跃维护，推荐使用** ✅

- **创建时间**：2019 年，已有约 6 年历史，属于成熟的 Virtual Production 核心工具
- **更新频率**：持续有功能性更新和 bug 修复，最近的 commit 涉及协议遮罩保存修复、编译警告修复、新调试命令等
- **维护状态**：由 Epic Games 官方维护，是 Virtual Production 工作流的核心组件
- **代码规模**：659 个源文件、8 个模块，架构完善且经过充分迭代
- **API 稳定性**：从代码中可见多处 `UE_DEPRECATED` 标记（如 `FRCMaskingOperation` 在 5.5 废弃、`ClearMask`/`EnableMask` 在 5.6 废弃），说明 API 在持续演进但保持向后兼容
- **已知限制**：
  - 部分旧 API（如全局 Masking）已废弃，需迁移到 per-protocol-binding masking
  - 虚拟属性系统依赖 StructUtils，需注意版本兼容
  - WebRemoteControl 模块在打包构建中需要额外配置

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/remote-control-api-in-unreal-engine/)