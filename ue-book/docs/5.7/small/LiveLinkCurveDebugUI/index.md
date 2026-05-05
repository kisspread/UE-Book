# Live Link Curve Debug UI

> Allows Viewing LiveLink Curve Debug Information

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | ❌ `CanContainContent: false` |
| 模块 | LiveLinkCurveDebugUI (Runtime, LoadingPhase: PreDefault) |
| 创建时间 | 2019-01-23 |
| 年龄标签 | 👴 老古董 (>5年) |
| 实验性 | ⚠️ `IsBetaVersion: true` |
| 插件依赖 | [LiveLink](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Animation/LiveLink/LiveLink.uplugin) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkCurveDebugUI) | |

## 用途

LiveLinkCurveDebugUI 提供了一个实时调试界面，用于可视化 LiveLink 传输的 Curve 数据。当你通过 LiveLink 接收面部捕捉（ARKit/ARCore blendshapes）、动画曲线或其他 float 类型的曲线值时，这个 plugin 会以一个带颜色渐变的进度条列表显示每条曲线的名称和当前值，方便你快速验证数据是否正确传输、数值范围是否合理。

核心解决的问题：LiveLink 曲线数据在传输过程中很难直观观察，这个 UI 让每条曲线都有一个实时刷新的可视化指示器。

## 使用场景

- 你在做面部动捕（Face AR），需要确认 LiveLink 源端的 blendshape 曲线是否正确映射到 UE5
- 你在调试 LiveLink 数据源，需要实时查看所有 curve 的数值变化
- 你需要在编辑器或运行时（游戏内）快速查看 LiveLink curve 数据，无需写蓝图或 C++ 代码
- 你需要验证新接入的 LiveLink 设备/软件发送的曲线数据是否在预期范围内

## 蓝图用法

> ⚠️ 此 plugin 默认关闭，需在 Edit → Plugins 中手动启用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Display Live Link Debugger` | 打开调试 UI，显示指定 Subject 的所有曲线 | `ULiveLinkDebuggerBlueprintLibrary` |
| `Hide Live Link Debugger` | 关闭调试 UI | `ULiveLinkDebuggerBlueprintLibrary` |
| `Get DPIScale Based On Size` | 根据屏幕分辨率计算 DPI 缩放 | `ULiveLinkDebuggerSettings` |
| `Get Bar Color For Curve Value` | 根据曲线值（0-1）获取对应的进度条颜色 | `ULiveLinkDebuggerSettings` |

### 使用示例

**打开调试 UI：**
1. 在蓝图中搜索 `Display Live Link Debugger` 节点
2. 连接一个包含 LiveLink Subject 名称的 String 变量（例如 `"FaceAR"`）
3. 运行后会在视口或编辑器 Tab 中显示曲线列表

**关闭调试 UI：**
- 调用 `Hide Live Link Debugger` 即可移除

### 设置项

在 Project Settings → Plugins → Live Link Debugger Settings 中可配置：

| 设置 | 说明 | 默认值 |
|---|---|---|
| Min Bar Color Value | 曲线值为 0 时进度条的颜色 | - |
| Max Bar Color Value | 曲线值为 1 时进度条的颜色 | - |
| DPI Scale Multiplier | 游戏内视口的 DPI 缩放倍数（比编辑器中更大） | - |

## C++ 用法

### 头文件引入

```cpp
#include "ILiveLinkCurveDebugUIModule.h"
#include "LiveLinkDebuggerBlueprintLibrary.h"
```

### 基本用法 — 通过模块接口控制

```cpp
// 获取模块实例
ILiveLinkCurveDebugUIModule& DebugModule = FModuleManager::GetModuleChecked<ILiveLinkCurveDebugUIModule>("LiveLinkCurveDebugUI");

// 显示调试 UI，传入要跟踪的 LiveLink Subject 名称
FString SubjectName = TEXT("FaceAR");
DebugModule.DisplayLiveLinkCurveDebugUI(SubjectName);

// 隐藏调试 UI
DebugModule.HideLiveLinkCurveDebugUI();
```

### 基本用法 — 通过蓝图库静态函数

```cpp
#include "LiveLinkDebuggerBlueprintLibrary.h"

// 显示
ULiveLinkDebuggerBlueprintLibrary::DisplayLiveLinkDebugger(TEXT("FaceAR"));

// 隐藏
ULiveLinkDebuggerBlueprintLibrary::HideLiveLinkDebugger();
```

### 控制台命令

模块继承了 `FSelfRegisteringExec`，支持通过控制台命令直接触发（参见 `LiveLinkCurveDebugUIModule.h` 中的 `Exec` 方法）。

### 自定义 Slate Widget

`SLiveLinkCurveDebugUI` 是核心 Slate widget，可嵌入到自定义编辑器工具中：

```cpp
#include "SLiveLinkCurveDebugUI.h"

// 创建 widget
TSharedRef<SLiveLinkCurveDebugUI> DebugWidget =
    SNew(SLiveLinkCurveDebugUI)
    .DPIScale(1.0f)
    .InitialLiveLinkSubjectName(FName("FaceAR"))
    .UpdateRate(0.1f)  // 每 0.1 秒刷新一次
    .ShowLiveLinkSubjectNameHeader(true);
```

## Demo 示例

### 最小蓝图示例

**场景：** 在 BeginPlay 时显示 LiveLink 曲线调试 UI

1. 创建一个 Actor Blueprint
2. 在 Event BeginPlay 之后连接 `Display Live Link Debugger` 节点
3. Subject Name 参数填入你的 LiveLink Subject 名称（如 `"FaceAR"`）
4. 放入场景，运行游戏，视口中会显示曲线列表

### 最小 C++ 示例

```cpp
// MyDebugActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyDebugActor.generated.h"

UCLASS()
class AMyDebugActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category = "LiveLink")
    FString SubjectName = TEXT("FaceAR");
};

// MyDebugActor.cpp
#include "MyDebugActor.h"
#include "LiveLinkDebuggerBlueprintLibrary.h"

void AMyDebugActor::BeginPlay()
{
    Super::BeginPlay();
    ULiveLinkDebuggerBlueprintLibrary::DisplayLiveLinkDebugger(SubjectName);
}

void AMyDebugActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    ULiveLinkDebuggerBlueprintLibrary::HideLiveLinkDebugger();
    Super::EndPlay(EndPlayReason);
}
```

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "LiveLinkCurveDebugUI"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、World 等） |
| `LiveLinkInterface` | LiveLink 接口定义（ILiveLinkClient 等） |
| `Slate` | UI 框架（列表视图、组合框等） |
| `SlateCore` | Slate 核心（样式、颜色等） |
| `InputCore` | 输入系统 |
| `EditorFramework` | （仅编辑器）编辑器框架 |
| `UnrealEd` | （仅编辑器）编辑器工具 |

## 源码结构

```
Source/LiveLinkCurveDebugUI/
├── Public/
│   ├── ILiveLinkCurveDebugUIModule.h    # 模块接口
│   ├── LiveLinkCurveDebugUIModule.h      # 模块实现声明
│   ├── LiveLinkDebuggerBlueprintLibrary.h # 蓝图函数库
│   ├── LiveLinkDebuggerSettings.h        # 设置（颜色、DPI）
│   ├── LiveLinkDebugCurveNodeBase.h      # 单条曲线数据节点
│   ├── SLiveLinkCurveDebugUI.h           # 核心 Slate widget
│   └── SLiveLinkCurveDebugUITab.h        # 带 Subject 选择器的 Tab
│   └── SLiveLinkCurveDebugUIListItem.h   # 列表中每一行的 widget
└── Private/
    └── (对应 .cpp 实现)
```

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2023-01-16 | `7ce67da` | IWYU 更新，减少不必要的 #include | 代码清理，无功能变化 |
| 2022-11-07 | `0a10c21` | Release-Engine-Staging 同步 | 批量更新，非针对性改动 |
| 2022-09-09 | `afc7435` | 修复编译问题 `-allmodules` | 编译兼容性修复 |

### 维护评价

- **创建时间**：2019 年 1 月，已超过 7 年
- **实验性标记**：`IsBetaVersion: true`，从未毕业为正式版本
- **默认关闭**：`EnabledByDefault: false`，需要手动启用
- **最近更新**：最后一次实质性更新在 2023 年初，且仅为 IWYU 代码清理；超过 2 年无功能更新
- **状态**：⚠️ 维护不活跃，可能已接近废弃
- **是否推荐使用**：可以使用，功能完整且稳定，但不要期待新功能。如果只需要简单的调试可视化，它是零代码的最佳选择；如果需要更高级的调试功能，建议自行扩展或使用 LiveLink 自带的其他工具

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkCurveDebugUI)
- [LiveLink Plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink)
