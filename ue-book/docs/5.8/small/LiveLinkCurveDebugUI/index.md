# Live Link Curve Debug UI

> Allows Viewing LiveLink Curve Debug Information

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接曲线调试界面 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkCurveDebugUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-23 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkCurveDebugUI) | |

## 用途

该插件的核心作用是提供一个**可交互的 UI 工具**，用于实时可视化并调试通过 LiveLink 接收的曲线（Curve）数据。在动画数据流（如动捕、面捕）的开发与调试过程中，开发者需要观察特定动画曲线（如 BlendShape、控制参数）的实时数值变化。此插件正是为此场景而生，它不仅仅是一个简单的数值显示器，还提供了可停靠的选项卡界面和直接附加到游戏视口的模式，方便开发者在编辑器内外进行调试。

## 使用场景

- 你正在使用 LiveLink 接收来自 iPhone 面捕（ARKit）或动作捕捉设备的面部或身体曲线数据，需要实时查看各个 BlendShape 或控制曲线的值是否符合预期。
- 你在调试 LiveLink 数据源（如虚拟摄像头、其他应用程序）时，需要一个快速、直观的界面来验证哪些曲线正在传输以及它们的数值。
- 你希望在 Play In Editor (PIE) 或独立的游戏窗口中直接叠加显示曲线数据，而无需频繁切换到专门的编辑器面板。

## 蓝图用法

该插件主要通过一个蓝图函数库暴露核心功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Display Live Link Debugger` | 显示 LiveLink 曲线调试界面。需要传入要观察的 LiveLink 主体名称。 | `ULiveLinkDebuggerBlueprintLibrary` |
| `Hide Live Link Debugger` | 隐藏当前显示的 LiveLink 曲线调试界面。 | `ULiveLinkDebuggerBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **在关卡蓝图或任意 Actor 的事件图表中**，右键搜索 `Display Live Link Debugger`。
2.  将其输出执行引脚连接到触发事件（如 `BeginPlay` 或一个按键事件）。
3.  为 `SubjectName` 参数输入一个字符串，对应你想要调试的 LiveLink 主体名称（例如 `“ARKitFace”`）。
4.  当需要隐藏时，调用 `Hide Live Link Debugger` 节点。

## C++ 用法

更底层的控制通过 C++ 模块接口 `ILiveLinkCurveDebugUIModule` 实现。

### 头文件引入

```cpp
#include "ILiveLinkCurveDebugUIModule.h"
```

### 基本用法

通过模块接口获取并控制调试 UI。以下是根据 `ILiveLinkCurveDebugUIModule.h` 和 `LiveLinkCurveDebugUIModule.h` 编写的示例：

```cpp
// 获取 LiveLinkCurveDebugUI 模块
ILiveLinkCurveDebugUIModule* CurveDebugModule = FModuleManager::GetModulePtr<ILiveLinkCurveDebugUIModule>(TEXT(“LiveLinkCurveDebugUI”));
if (CurveDebugModule)
{
    // 显示指定 LiveLink 主体的调试 UI
    FString SubjectName = TEXT(“MyLiveLinkSubject”);
    CurveDebugModule->DisplayLiveLinkCurveDebugUI(SubjectName);

    // … 在之后的某个时刻 …
    // 隐藏调试 UI
    CurveDebugModule->HideLiveLinkCurveDebugUI();
}
```

### 进阶用法

该模块还提供了管理选项卡生成功能，这在你希望将调试界面作为编辑器的一个标准标签页时非常有用：

```cpp
// 注册标签页生成器，使其出现在“窗口”菜单等位置
CurveDebugModule->RegisterTabSpawner();

// … 在插件或模块关闭时 …
// 注销标签页生成器
CurveDebugModule->UnregisterTabSpawner();
```

## Demo 示例

以下是一个最简单的、可在任何 Actor 或 GameMode 中使用的 C++ 示例，用于显示和隐藏 LiveLink 曲线调试 UI。

**MyActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include “GameFramework/Actor.h”
#include “MyActor.generated.h”

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    UFUNCTION(BlueprintCallable, Category = “Debug”)
    void ShowLiveLinkDebug();

    UFUNCTION(BlueprintCallable, Category = “Debug”)
    void HideLiveLinkDebug();

private:
    bool bIsDebugUIVisible;
};
```

**MyActor.cpp**
```cpp
#include “MyActor.h”
#include “ILiveLinkCurveDebugUIModule.h”

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = true;
    bIsDebugUIVisible = false;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    // 可在此初始化LiveLink连接等
}

void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void AMyActor::ShowLiveLinkDebug()
{
    if (!bIsDebugUIVisible)
    {
        if (ILiveLinkCurveDebugUIModule* CurveDebugModule = FModuleManager::GetModulePtr<ILiveLinkCurveDebugUIModule>(TEXT(“LiveLinkCurveDebugUI”)))
        {
            FString SubjectToTrack = TEXT(“MyARKitFace”); // 替换为你的实际LiveLink主体名
            CurveDebugModule->DisplayLiveLinkCurveDebugUI(SubjectToTrack);
            bIsDebugUIVisible = true;
        }
    }
}

void AMyActor::HideLiveLinkDebug()
{
    if (bIsDebugUIVisible)
    {
        if (ILiveLinkCurveDebugUIModule* CurveDebugModule = FModuleManager::GetModulePtr<ILiveLinkCurveDebugUIModule>(TEXT(“LiveLinkCurveDebugUI”)))
        {
            CurveDebugModule->HideLiveLinkCurveDebugUI();
            bIsDebugUIVisible = false;
        }
    }
}
```

## 模块依赖

该插件本身依赖于 `LiveLink` 插件。若要使用此插件或基于其代码进行开发，你的项目模块需要包含以下依赖（在 `.Build.cs` 文件中添加）：

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心 LiveLink 框架，本插件依赖此模块获取动画数据流。 |
| `EditorFramework` | 用于支持编辑器内的选项卡（Tab）系统和界面管理。 |
| `UnrealEd` | 编辑器核心功能，支持在编辑器中注册菜单项、选项卡生成器等。 |

**注意**：由于该模块类型为 `Runtime` 但依赖 `EditorFramework` 和 `UnrealEd`，它通常仅在编辑器环境下使用（或 `WITH_EDITOR` 宏生效时）。在纯运行时打包中可能无法正常工作。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏 UE_LOG 迁移为新的 UE_LOGF 格式。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录结构调整，可能涉及路径更新。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的引用链接，使用更安全的协议。 |
| 2022-09-10 | `eb252c5a` | Fixed some issues not found from PF when compiling with -allmodules. | 修复了使用“-allmodules”参数编译时发现的一些问题。 |
| 2022-09-10 | `7b9e5abb` | Pass 1 on plugins: | 对插件进行第一轮代码审查或重构。 |

### 维护评价

该插件**创建于 2019 年，历史较长**。从 Git 记录看，其核心功能在初始提交后没有发生重大变化或增强。最近的提交（`35e60df1`，2026年）仅为日志宏的代码风格迁移，属于全局维护性修改，并非针对该插件的功能更新。其余更早的提交也主要是全局的编译修复、协议更新或目录结构调整，**没有任何实质性的功能迭代或 bug 修复记录**。

虽然它仍能编译通过并存在于引擎中，但标记为 `IsBetaVersion: true`，且长期缺乏维护。它更像是一个**历史遗留的调试工具**，功能相对基础且固定。对于新的 LiveLink 调试需求，建议优先考虑引擎后续版本中可能提供的更现代、功能更丰富的工具或直接使用 `LiveLink` 插件自身的可视化功能。

**综上所述，该插件处于“维护不活跃”状态，可以临时用于调试目的，但不推荐作为生产流程或长期项目的核心依赖。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkCurveDebugUI)
- [LiveLink 插件文档](https://docs.unrealengine.com/5.8/en-US/live-link-in-unreal-engine/) (父级功能文档)