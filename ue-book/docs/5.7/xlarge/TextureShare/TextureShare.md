# Texture Share

> Share textures and data between processes

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `TextureShareCore` (Runtime), `TextureShare` (Runtime), `TextureShareDisplayCluster` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/TextureShare) | |

## 用途

TextureShare 插件为 Unreal Engine 提供了一套进程间纹理与数据共享的框架。它主要用于解决虚拟制作（Virtual Production）中，多个独立进程（例如运行在不同机器上的 nDisplay 渲染节点、外部合成软件或自定义工具）需要实时交换渲染结果或自定义数据的问题。

其核心价值在于：
1.  **跨进程通信**：通过共享内存（Shared Memory）等机制，实现低延迟的进程间数据传输。
2.  **纹理同步**：允许一个进程将渲染好的纹理（如 `UTexture`）发送给其他进程，并在接收端将其映射为 `UTextureRenderTarget` 以供后续处理或显示。
3.  **数据交换**：除了纹理，还可以交换键值对形式的自定义数据（`TMap<FString, FString>`），用于传递状态、参数等信息。
4.  **与 nDisplay 集成**：专门提供了 `TextureShareDisplayCluster` 模块，用于与 nDisplay 插件深度集成，简化多机渲染同步的配置。

## 使用场景

-   **nDisplay 多机渲染**：在由多台 PC 组成的 nDisplay 集群中，主控机需要将特定视图的渲染结果（如 UI 层、合成层）实时共享给其他渲染节点。
-   **外部合成软件集成**：将 UE 的实时渲染画面（如最终合成后的画面）实时发送给 Nuke、After Effects 等合成软件，进行实时预览或进一步处理。
-   **自定义工具链**：开发独立的监控、调试或控制工具，这些工具需要读取 UE 进程内部的渲染画面或状态数据。
-   **进程间数据同步**：在多个 UE 实例或 UE 与非 UE 应用之间同步游戏状态、配置参数等。

## 蓝图用法

插件提供了 `UTextureShare` 和 `UTextureShareObject` 两个主要的蓝图可用类，用于在蓝图中配置和管理纹理共享。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get or Create TextureShare Object` | 根据名称获取或创建一个共享对象实例。 | `UTextureShare` |
| `Remove TextureShare Object` | 根据名称移除一个共享对象。 | `UTextureShare` |
| `Get All TextureShare Objects` | 获取所有已创建的共享对象列表。 | `UTextureShare` |
| `Send Custom Data` | 向关联的共享对象发送自定义键值对数据。 | `UTextureShareObject` |

### 使用示例（蓝图描述）

1.  **创建共享对象**：
    *   在你的 Actor 或 Widget 蓝图中，添加一个 `UTextureShare` 类型的变量（例如命名为 `MyTextureShare`）。
    *   在事件图表中，调用 `MyTextureShare` 的 `Get or Create TextureShare Object` 节点，传入一个唯一的字符串名称（如 `"MySharedView"`），将返回的 `UTextureShareObject` 保存到变量中。

2.  **配置共享纹理**：
    *   在 `UTextureShareObject` 变量的细节面板中，展开 `Textures` 属性。
    *   在 `SendTextures` 数组中添加元素，为每个元素指定一个 `Name`（用于IPC标识）和要发送的 `UTexture`（如一个 `TextureRenderTarget2D`）。
    *   在 `ReceiveTextures` 数组中添加元素，为每个元素指定一个 `Name` 和一个用于接收的 `UTextureRenderTarget` 资产。

3.  **发送自定义数据**：
    *   调用 `UTextureShareObject` 的 `Send Custom Data` 节点，传入一个 `TMap<FString, FString>` 类型的变量，其中包含你想要发送的键值对数据。

4.  **启用/禁用**：
    *   通过设置 `UTextureShare` 的 `bEnable` 属性和每个 `UTextureShareObject` 的 `bEnable` 属性，可以全局或单独控制共享的开关。

## C++ 用法

### 头文件引入

```cpp
#include "ITextureShare.h"
#include "ITextureShareAPI.h"
```

### 基本用法

以下代码展示了如何在 C++ 中初始化 TextureShare 模块并创建一个共享对象。

```cpp
// 确保模块已加载
if (ITextureShare::IsAvailable())
{
    // 获取模块接口
    ITextureShare& TextureShareModule = ITextureShare::Get();
    
    // 获取核心 API 接口
    ITextureShareAPI& TextureShareAPI = TextureShareModule.GetTextureShareAPI();
    
    // 创建一个共享对象，名称为 "MyCppSharedObject"
    // 注意：实际 API 可能更复杂，此处为概念示例
    // TSharedPtr<ITextureShareObject> SharedObject = TextureShareAPI.CreateShareObject(TEXT("MyCppSharedObject"));
    
    // 配置对象（具体 API 需查阅 ITextureShareAPI 头文件）
    // SharedObject->SetEnabled(true);
    // SharedObject->AddSendTexture(TEXT("SceneColor"), MySceneColorTexture);
    // SharedObject->AddReceiveTexture(TEXT("ExternalUI"), MyRenderTarget);
    
    // 发送自定义数据
    // TMap<FString, FString> CustomData;
    // CustomData.Add(TEXT("FrameNumber"), FString::FromInt(GFrameNumber));
    // SharedObject->SendCustomData(CustomData);
}
```

### 进阶用法

TextureShare 的设计支持多线程。`ITextureShareContext` 类用于在游戏线程和渲染线程之间安全地传递数据。通常，你需要为你的特定实现（如基于 `UWorldSubsystem`）创建一个继承自 `ITextureShareContext` 的子类，并在其中实现回调逻辑。

```cpp
// 自定义上下文类
class FMyTextureShareContext : public ITextureShareContext
{
public:
    virtual FName GetRTTI() const override { return TEXT("MyCustomContext"); }
    
    // 实现游戏线程的回调注册
    virtual void RegisterTextureShareContextCallbacks() override
    {
        // 在这里绑定你的游戏线程回调函数
    }
    
    // 实现渲染线程的回调注册
    virtual void RegisterTextureShareContextCallbacks_RenderThread() override
    {
        // 在这里绑定你的渲染线程回调函数
    }
};

// 在每帧更新时，创建新的上下文并设置给共享对象
// TSharedPtr<FMyTextureShareContext> NewContext = MakeShared<FMyTextureShareContext>();
// SharedObject->SetTextureShareContext(NewContext);
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何创建一个 TextureShare 对象并配置其发送一个纹理。

**MyTextureShareActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTextureShareActor.generated.h"

class UTextureShareObject;

UCLASS()
class AMyTextureShareActor : public AActor
{
    GENERATED_BODY()

public:
    AMyTextureShareActor();

protected:
    virtual void BeginPlay() override;

public:
    // 要发送的纹理（在编辑器中指定）
    UPROPERTY(EditAnywhere, Category = "TextureShare")
    UTexture* TextureToSend;

    // TextureShare 对象名称
    UPROPERTY(EditAnywhere, Category = "TextureShare")
    FString ShareObjectName = TEXT("DemoShare");

private:
    UPROPERTY()
    TObjectPtr<UTextureShareObject> ShareObject;
};
```

**MyTextureShareActor.cpp**
```cpp
#include "MyTextureShareActor.h"
#include "Blueprints/TextureShareBlueprintContainers.h"

AMyTextureShareActor::AMyTextureShareActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyTextureShareActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建 TextureShare 管理器（通常作为组件或子系统存在，此处为简化）
    // 在实际项目中，你可能会从某个管理器获取或创建 UTextureShare 实例。
    UTextureShare* TextureShareManager = NewObject<UTextureShare>(this);
    TextureShareManager->bEnable = true;

    // 创建或获取共享对象
    ShareObject = TextureShareManager->GetOrCreateTextureShareObject(ShareObjectName);
    if (ShareObject)
    {
        ShareObject->bEnable = true;
        
        // 配置要发送的纹理
        FTextureShareSendTextureDesc SendDesc;
        SendDesc.Name = TEXT("SceneTexture");
        SendDesc.Texture = TextureToSend;
        ShareObject->Textures.SendTextures.Add(SendDesc);

        // 发送一些初始自定义数据
        TMap<FString, FString> InitialData;
        InitialData.Add(TEXT("ActorName"), GetName());
        ShareObject->SendCustomData(InitialData);

        UE_LOG(LogTemp, Log, TEXT("TextureShare object '%s' configured."), *ShareObjectName);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TextureShareCore` | 提供纹理共享的核心逻辑、IPC 通信和数据结构。 |
| `DisplayCluster` | 用于与 nDisplay 插件集成，实现多机渲染同步。 |

## 维护状态

### 近期更新

```
- d7bd17da4937 Don't include windows things if not windows
- 32884de457cd Changing more uses of RHICreateTexture to RHICmdList.CreateTexture.
- ea97db608460 Movie Render Queue:  High-res tiling support for paging scene view state persistent data to system memory, allowing significantly higher resolutions to be rendered by exceeding what would fit in GPU memory.  On a CitySample test sequence, a PC with 256 GB system memory and 48 GB GPU memory was able to render at double the maximum resolution (23040x12960 -> 46080x25920).  Performance cost per pixel is roughly 3x higher, bottlenecked by the added GPU cost of the transfers (mostly the readbacks).
```

*   `d7bd17da4937`: 平台兼容性修复，确保非 Windows 平台编译通过。
*   `32884de457cd`: 引擎内部 RHI API 的迁移，将 `RHICreateTexture` 改为使用 `RHICmdList.CreateTexture`，属于底层维护性更新。
*   `ea97db608460`: 这是一个大型功能提交，主要针对 Movie Render Queue 的高分辨率渲染支持。虽然不直接属于 TextureShare 插件，但表明该插件所在的代码库（VirtualProduction）仍在积极开发和优化中。

### 维护评价

TextureShare 插件创建于 2020 年，已有约 5 年历史。从最近的提交记录看，它仍在接受维护性更新（如平台兼容性修复、API 迁移），但近期没有重大的功能增强。其状态标记为 `IsBetaVersion: true` 且默认禁用，表明 Epic 可能认为它尚未达到完全稳定的生产就绪状态，或者其使用场景相对专一。

**结论**：该插件仍在维护中，没有被废弃的迹象。对于需要在 UE 进程间进行纹理和数据共享的虚拟制作项目（尤其是基于 nDisplay 的），它是一个官方提供的可行方案。但由于其 Beta 状态和默认禁用的设置，使用者需要自行评估其稳定性，并做好可能遇到边界问题的准备。推荐在明确需要此功能的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/TextureShare)
- [官方文档]() (无)
- [测试用例]() (未在提供信息中明确路径)