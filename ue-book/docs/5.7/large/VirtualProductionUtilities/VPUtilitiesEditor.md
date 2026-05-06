# Virtual Production Utilities

> Utility classes and functions for Virtual Production

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制片工具集 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器脚本） |
| 模块 | `VPUtilities` (Runtime), `VPUtilitiesEditor` (Runtime), `VPBookmark` (Runtime), `VPBookmarkEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities) | |

---

## 用途

本插件为虚幻引擎的虚拟制片工作流提供了一系列实用工具和编辑器扩展，主要聚焦于：

- **编辑器内时间同步与帧率管理**：提供 `Genlock Provider` 和 `Timecode Provider` 的可视化状态显示，帮助团队成员实时掌握时间码与同步状态。
- **编辑器可标记演员系统**：提供可在编辑器视口中接收 `EditorTick` 并保存/不保存至关卡的两类抽象演员基类，用于实现临时场景对象、测量工具、VR 交互代理等。
- **OSC 服务器集成**：在编辑器启动时自动启动 OSC 服务器，并支持绑定 OSC 监听器蓝图对象，便于通过外部设备（如平板、手机）控制虚拟制片。
- **虚拟场景外景辅助**：已废弃的 VR 外景子系统（`VPScoutingSubsystem`）和 VR 工具基类（`AVRTool`）将在 UE5.7 中彻底移除，**新项目不应使用**。

> ⚠️ **实验性警告**：该插件标记为 Beta 版本，大量旧代码（VR Scouting、Gesture Manager 等）已在 UE5.5 中被废弃，并将在 UE5.7 中移除。建议仅使用最新提供的功能（如 Timecode Provider 显示、OSC 服务器、可编辑 Tick Actor）。

---

## 使用场景

- **影视虚拟制片**：需要在 Unreal Engine 编辑器中与真实摄像机/外部设备同步时间码和帧率，并在 UI 上实时显示同步状态。
- **编辑内临时工具**：需要创建只在编辑器中活动的临时几何体、测量辅助线、标注点，这些对象在保存关卡时不应被持久化。
- **外部控制集成**：通过 OSC 协议从 iPad 或触控面板控制编辑器中的摄像机、灯光或场景元素，而不需要额外插件。
- **快速截图存储**：将编辑器视口截图直接导入为纹理资产，用于虚拟制片中的镜头预览或记录。

---

## 蓝图用法

本模块的蓝图函数库为 `UVPUtilitiesEditorBlueprintLibrary`，主要提供以下可调用节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn VP Editor Tickable Actor` | 在编辑器中生成一个会收 `EditorTick` 的非临时演员（保存至关卡） | `UVPUtilitiesEditorBlueprintLibrary` |
| `Spawn VP Transient Editor Tickable Actor` | 在编辑器中生成一个临时演员（不保存至关卡，也不会同步至多用户） | `UVPUtilitiesEditorBlueprintLibrary` |
| `Import Snapshot Texture` | 将指定绝对路径的图片文件导入到 `/Game/VirtualProduction/Snapshots/` 下，返回 `UTexture` 对象 | `UVPUtilitiesEditorBlueprintLibrary` |
| `Get Default OSC Server` | 获取模块启动时创建的默认 OSC 服务器对象 `UOSCServer` | `UVPUtilitiesEditorBlueprintLibrary` |

### 使用示例（蓝图）

1. **生成临时 Tick 演员**：将 `Spawn VP Transient Editor Tickable Actor` 节点拖入蓝图，连接 `Event BeginPlay` 或 `Event EditorTick`（在编辑器初始化时生成），指定一个继承自 `AVPTransientEditorTickableActorBase` 的蓝图类，并输入位置和旋转。
2. **导入截图**：使用 `Import Snapshot Texture` 节点，将文件路径传入（例如 `C:/Temp/Screenshot.png`），返回的纹理可直接用于材质或 UI。
3. **获取 OSC 服务器并绑定监听器**：调用 `Get Default OSC Server` 获得服务器对象，然后配置其监听地址和端口（参考 OSC 模块用法）。

> 注意：`Spawn VP Editor Tickable Actor` 生成的演员会保存在关卡中，适用于需要持久化的编辑器辅助对象；`Spawn VP Transient Editor Tickable Actor` 则适用于临时工具。

---

## C++ 用法

### 头文件引入

```cpp
#include "VPUtilitiesEditorBlueprintLibrary.h"
#include "VPEditorTickableActorBase.h"
#include "VPTransientEditorTickableActorBase.h"
#include "IVPUtilitiesEditorModule.h"
```

### 基本用法

**1. 生成编辑器 Tick 演员**

```cpp
// 在任意 UObject 中（例如 GameInstance、EditorSubsystem）
class UVPUtilitiesEditorBlueprintLibrary* Lib = GetMutableDefault<UVPUtilitiesEditorBlueprintLibrary>();
UObject* Context = GetWorld();
FVector Location = FVector::ZeroVector;
FRotator Rotation = FRotator::ZeroRotator;
TSubclassOf<AVPEditorTickableActorBase> Class = AMyEditorTickableActor::StaticClass();

AVPEditorTickableActorBase* Actor = UVPUtilitiesEditorBlueprintLibrary::SpawnVPEditorTickableActor(Context, Class, Location, Rotation);
if (Actor)
{
    // Actor 会收到 EditorTick 调用
}
```

**2. 获取默认 OSC 服务器**

```cpp
IVPUtilitiesEditorModule& VPUtilitiesModule = IVPUtilitiesEditorModule::Get();
UOSCServer* OSCServer = VPUtilitiesModule.GetOSCServer();
if (OSCServer)
{
    // 配置服务器监听地址
    OSCServer->SetAddress("0.0.0.0", 8000);
    OSCServer->Listen();
}
```

**3. 导入截图纹理**

```cpp
UTexture* ImportedTexture = UVPUtilitiesEditorBlueprintLibrary::ImportSnapshotTexture(
    TEXT("Frame_001.png"),
    TEXT("Session_2025"),
    TEXT("C:/Unreal/Snapshots/")
);
if (ImportedTexture)
{
    // 使用纹理
}
```

### 进阶用法

**自定义编辑器 Tick 演员**

继承 `AVPEditorTickableActorBase` 或 `AVPTransientEditorTickableActorBase`，并重写 `EditorTick` 方法（在 `AVPViewportTickableActorBase` 中定义）。

```cpp
// MyEditorTickActor.h
#pragma once

#include "VPTransientEditorTickableActorBase.h"
#include "MyEditorTickActor.generated.h"

UCLASS(Transient)
class AMyEditorTickActor : public AVPTransientEditorTickableActorBase
{
    GENERATED_BODY()

public:
    // 编辑器每帧调用
    virtual void EditorTick_Implementation(float DeltaSeconds) override
    {
        Super::EditorTick_Implementation(DeltaSeconds);
        // 在这里执行自定义逻辑，例如移动、测量
        UE_LOG(LogTemp, Log, TEXT("Editor tick ticked!"));
    }
};
```

**创建 OSC 监听器**

在 `UVPUtilitiesEditorSettings` 中配置 `StartupOSCListeners` 数组，指向继承自 `UEditorUtilityObject` 的蓝图，模块启动时会自动执行这些对象，从而绑定 OSC 消息处理。

```cpp
// 可以在 EditorUtilityObject 蓝图里重载 Run()，在其中订阅 OSC 消息
UCLASS()
class UMyOSCListener : public UEditorUtilityObject
{
    GENERATED_BODY()

    virtual void Run() override
    {
        UOSCServer* Server = IVPUtilitiesEditorModule::Get().GetOSCServer();
        if (Server)
        {
            Server->OnOscMessageReceived.AddDynamic(this, &UMyOSCListener::HandleMessage);
        }
    }

    UFUNCTION()
    void HandleMessage(const FOSCMessage& Message, const FString& IPAddress, uint16 Port)
    {
        // 处理 OSC 消息
    }
};
```

---

## Demo 示例

以下是一个最小可编译的 C++ 模块示例，演示如何使用 `VPTransientEditorTickableActorBase` 创建一个在编辑器视口中持续旋转的立方体。

**MyActor.h**

```cpp
#pragma once

#include "VPTransientEditorTickableActorBase.h"
#include "Components/StaticMeshComponent.h"
#include "MyActor.generated.h"

UCLASS(Transient)
class AMyRotatingCube : public AVPTransientEditorTickableActorBase
{
    GENERATED_BODY()

public:
    AMyRotatingCube()
    {
        Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
        SetRootComponent(Root);

        Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
        Mesh->SetupAttachment(Root);

        bIsEditorOnlyActor = true;
        PrimaryActorTick.bStartWithTickEnabled = true;
    }

    virtual void EditorTick_Implementation(float DeltaSeconds) override
    {
        Super::EditorTick_Implementation(DeltaSeconds);
        if (Mesh)
        {
            FRotator NewRot = Mesh->GetRelativeRotation() + FRotator(0, DeltaSeconds * 45.0f, 0);
            Mesh->SetRelativeRotation(NewRot);
        }
    }

private:
    UPROPERTY()
    TObjectPtr<USceneComponent> Root;

    UPROPERTY()
    TObjectPtr<UStaticMeshComponent> Mesh;
};
```

**MyModule.h**（用于生成演员的代码）

```cpp
// 在某个编辑器模块的 StartupModule 中生成
#include "MyActor.h"
#include "VPUtilitiesEditorBlueprintLibrary.h"

void FMyModule::StartupModule()
{
    AVPRotatingCube* Cube = UVPUtilitiesEditorBlueprintLibrary::SpawnVPTransientEditorTickableActor(
        GetWorld(),
        AMyRotatingCube::StaticClass(),
        FVector(100, 0, 100),
        FRotator::ZeroRotator
    );
}
```

> 注意：需要在模块的 Build.cs 中添加对 `VPUtilitiesEditor` 的依赖（见下节）。

---

## 模块依赖

`VPUtilitiesEditor` 独特的依赖项：

| 模块 | 用途 |
|---|---|
| `VPUtilities` | 运行时基础工具，如时间码提供器、OSC 服务器 |
| `OSC` | 提供 `UOSCServer` 类用于网络通信 |
| `Blutility` | 用于 `UEditorUtilityWidget` 和 `UEditorUtilityObject` 的支持 |
| `PlacementMode` | 用于注册“虚拟制片”放置类别 |
| `UnrealEd` | 编辑器基础，如 `FEditorDelegates`、`FPlacementCategoryInfo` |

**常见依赖未列出**：`Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `InputCore`, `EditorStyle`, `PropertyEditor`, `Projects`, `DeveloperSettings`。

---

## 维护状态

### 近期更新

- **2025-10-03** `e6b6696` — Fix full screen widget for media output providers（修复媒体输出提供者的全屏控件）
- **2025-09-25** `4b556c0` — VPUtilities OSC Server - Allow specifying an override for the server address（允许指定 OSC 服务器地址覆盖）
- **2025-09-23** `66f6004` — ViewportInteraction: Deprecate ViewportInteraction module alongside VR Editor（弃用 ViewportInteraction 模块）
- **2025-09-10** `cb5faa0` — VR Editor: Deprecate VR Editor mode and most associated classes（弃用 VR 编辑器模式及相关类）
- **2025-08-27** `551d3a5b` — Address bug hawk and CIS deprecation warnings（修复静态分析警告和弃用警告）

### 维护评价

- **活跃度**：插件仍在积极维护，最近一个月有功能性更新（OSC 地址覆盖）和 bug 修复。
- **弃用情况**：大量 VR 外景相关代码（`VPScoutingSubsystem`、`AVRTool`、`VPScoutingSubsystemHelpersBase`、`VPScoutingSubsystemGestureManagerBase`）已在 UE5.5 废弃，并明确将在 UE5.7 移除。**新项目应避免使用这些类**，而使用新提供的 `AVPEditorTickableActorBase` 和 `AVPTransientEditorTickableActorBase`。
- **推荐使用**：适用于希望在 UE5.6+ 中使用时间码同步、OSC 控制和编辑器 Tick 演员的虚拟制片项目。但需注意跳过废弃功能。
- **已知限制**：OSC 服务器默认绑定到 0.0.0.0，可能带来安全风险；`ImportSnapshotTexture` 仅支持导入到固定路径。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities)
- [官方文档（暂无）]()
- [测试用例（本插件暂未提供独立测试）]()