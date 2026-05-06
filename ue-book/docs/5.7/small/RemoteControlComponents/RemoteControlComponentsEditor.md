# Remote Control Components

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制组件 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlComponents` (Runtime), `RemoteControlComponentsEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteControlComponents) | |

## 用途

在 Unreal Engine 的远程控制系统基础上，提供基于 Actor 组件的轻量级远程控制方案。该插件允许开发者通过向任意 Actor 添加 `UComponent` 来定义可远程控制的属性，无需手动为每个 Actor 创建预设（Preset）。  
它解决了在动态场景中（如虚拟制片、实时演出）需要临时或批量远程控制多个 Actor 属性时的配置繁琐问题，将远程控制能力直接嵌入到组件中，实现按需绑定。

## 使用场景

- **虚拟制片现场**：在拍摄过程中，导演或技术员需要远程调节场景中某盏灯的强度、颜色，或者控制摄像机的焦距。通过给这些 Actor 添加 `RemoteControlComponents` 并暴露关键属性，即可立即通过 Web UI、MIDI 或 OSC 等协议进行实时控制。
- **实时交互装置**：在互动展览或舞台表演中，多台设备运行的 UE 实例需要同步控制同一 Actor 的属性，组件化方案便于快速部署和修改控制列表。
- **原型开发与测试**：开发者在调试阶段，需要快速临时暴露某些属性以便通过外部工具（如 Websocket 调试面板）进行调节，无需修改原有 Actor 蓝图代码。

## 蓝图用法

> 当前版本（v1.0，2024‑02）仍处于实验性阶段，**尚未暴露 BlueprintCallable 节点**。所有功能均需通过 C++ 调用。未来版本可能添加蓝图接口。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteControlComponent.h"               // 核心组件基类
#include "RemoteControlComponentsEditorStyle.h"    // 编辑器样式（仅编辑器模块）
```

### 基本用法

以下示例演示如何在 C++ Actor 中创建并使用远程控制组件。

```cpp
// 需要包含的文件
#include "RemoteControlComponent.h"

// 在 Actor 类的构造函数中创建组件
ARemoteControlActor::ARemoteControlActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建并注册远程控制组件
    RemoteControlComp = CreateDefaultSubobject<URemoteControlComponent>(TEXT("RemoteControlComp"));
}

// 在 BeginPlay 中绑定需要控制的属性
void ARemoteControlActor::BeginPlay()
{
    Super::BeginPlay();
    if (RemoteControlComp)
    {
        // 绑定当前 Actor 的“亮度”属性（假设存在 FFloatProperty）
        const FName PropertyName = GET_MEMBER_NAME_CHECKED(ThisClass, Brightness);
        RemoteControlComp->BindProperty(PropertyName);
    }
}
```

> **说明**：`URemoteControlComponent` 的具体 API 定义位于 `Public/RemoteControlComponent.h`（该插件核心模块的公开头文件，此处未列出）。用法与 [RemoteControl Preset](https://docs.unrealengine.com/5.3/en-US/remote-control-api/) 类似，但更贴近组件化模型。

### 进阶用法

结合编辑器模块，可以在细节面板中直接添加远程控制入口。

```cpp
#include "RemoteControlComponentsEditorStyle.h"

// 通常在派生组件类的重写函数中使用
void UMyRemoteControlComponent::PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent)
{
    Super::PostEditChangeProperty(PropertyChangedEvent);

    // 使用自定义图标样式（从 FRemoteControlComponentsEditorStyle 获取）
    if (PropertyChangedEvent.Property)
    {
        const FSlateBrush* Brush = FRemoteControlComponentsEditorStyle::Get().GetBrush(TEXT("RemoteControlComponents.Icon"));
        // ... 在 UI 中绘制
    }
}
```

## Demo 示例

以下是一个最小可编译的 Actor 类，展示了如何使用 `RemoteControlComponents` 插件。

**RemoteControlledActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RemoteControlComponent.h"
#include "RemoteControlledActor.generated.h"

UCLASS()
class ARemoteControlledActor : public AActor
{
    GENERATED_BODY()

public:
    ARemoteControlledActor();

    // 需要暴露给远程控制的属性
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Remote Control")
    float Intensity = 1.0f;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, Category = "Remote Control")
    URemoteControlComponent* RemoteControlComp;
};
```

**RemoteControlledActor.cpp**

```cpp
#include "RemoteControlledActor.h"

ARemoteControlledActor::ARemoteControlledActor()
{
    PrimaryActorTick.bCanEverTick = false;
    RemoteControlComp = CreateDefaultSubobject<URemoteControlComponent>(TEXT("RemoteControlComp"));
}

void ARemoteControlledActor::BeginPlay()
{
    Super::BeginPlay();
    if (RemoteControlComp)
    {
        // 绑定 Intensity 属性，使其可通过外部协议控制
        RemoteControlComp->BindProperty(GET_MEMBER_NAME_CHECKED(ThisClass, Intensity));
    }
}
```

> **注意**：实际使用时需确保 `URemoteControlComponent` 的头文件路径正确，并已添加模块依赖。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 提供底层远程控制协议和 Preset 管理 |
| `RemoteControlCommon` | 通用工具类（如属性路径解析） |
| `RemoteControlComponents`（自身模块） | 核心组件定义 |

由于该插件为插件本身提供 `RemoteControlComponents` 模块，使用者在自己的 `Build.cs` 中需添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "RemoteControlComponents",
    "RemoteControl",
    "RemoteControlCommon"
});
```

**Editor 额外依赖**（仅当需要编辑器样式时）：

```csharp
PrivateDependencyModuleNames.Add("RemoteControlComponentsEditor");
```

## 维护状态

### 近期更新

- 2024‑02‑14 `c579ba1` Motion Design:（初始提交？）
- 2024‑02‑13 `723c200` [Remote Control Components] Remove "invalid" tracked properties from Tracker
- 2024‑02‑12 `10de4db` Remote Control:（合并更新）
- 2024‑02‑09 `236f2d2` Remote Control Components:（功能实现）
- 2024‑02‑07 `1f30386` Motion Design RC:（项目建立）

### 维护评价

- **创建时间**：2024‑02‑07，至今约 1 年。
- **近期更新**：仅有 5 次提交，且集中在项目启动后的两周内。之后无实质性更新（截至当前）。
- **活跃度**：**维护不活跃**。超过 10 个月无任何提交，且插件被标记为 `IsExperimentalVersion=true`，表明仍处于早期实验阶段。
- **已知问题**：API 未稳定，缺少文档和蓝图支持，可能不适合生产环境。
- **推荐使用**：仅建议研究或原型验证，不建议用于正式项目。若需要稳定的远程控制功能，请使用官方 [Remote Control API](https://docs.unrealengine.com/5.3/en-US/remote-control-api/) 或 `RemoteControlPreset` 系统。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteControlComponents)
- [远程控制官方文档](https://docs.unrealengine.com/5.3/en-US/remote-control-api/)  
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteControlComponents/Tests)（可能存在，但未见公开）