# Virtual Production Utilities

> Utility classes and functions for Virtual Production

| 属性 | 值 |
|---|---|
| 中文名 | VP 书签 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器功能） |
| 模块 | `VPBookmark` (Runtime), `VPBookmarkEditor` (Runtime), `VPUtilities` (Runtime), `VPUtilitiesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities) | |

---

## 用途

虚拟制作书签模块（VPBookmark）提供一种**增强型书签系统**，专门用于虚拟制作工作流。与普通地图书签不同，VP 书签能够：

- 保存视口视角（位置、旋转、正交缩放）  
- 与场景中的 **Actor 关联**，书签激活/切换时自动触发 Actor 的行为（通过 `IVPBookmarkProvider` 接口）  
- 支持**分类管理**（CategoryName）和**显示名称生成**  
- 提供**生命周期委托**（创建、销毁、清除），便于编辑器工具集成  

该模块解决的核心问题是：在虚拟制作过程中，导演或操作员需要在不同摄像机位置、场景状态之间快速跳转，同时希望跳转后关联的 Actor（如灯光、道具、虚拟摄像机）自动响应（如激活/停用/修改参数）。普通的 `UBookmarkBase` 不具备这种动态关联能力。

---

## 使用场景

- **虚拟摄制组**：在不同取景机位之间切换，同时自动设置灯光、摄像机参数  
- **彩排与预演**：标记关键场景状态（如演员站位、特效触发点），一键恢复  
- **多用户协作（Concert）**：记录创建者的用户名，便于追踪修改来源  
- **自动化工具**：通过蓝图或 C++ 批量创建、删除、查询书签  

---

## 蓝图用法

所有公开的蓝图可调用 API 均来自 `UVPBookmark` 和 `UVPBookmarkBlueprintLibrary`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find VP Bookmark` | 根据 Actor 查找其关联的 VPBookmark 对象 | `UVPBookmarkBlueprintLibrary` |
| `Get All VP Bookmark Actors` | 获取当前世界中所有带有 VP 书签的 Actor 数组 | `UVPBookmarkBlueprintLibrary` |
| `Get All VP Bookmark` | 获取当前世界中所有 VP 书签对象 | `UVPBookmarkBlueprintLibrary` |
| `Create VP Bookmark Name` | 根据格式字符串生成书签的编号和字母（用于自动命名） | `UVPBookmarkBlueprintLibrary` |
| `Is Active` | 检查书签当前是否为激活状态 | `UVPBookmark` |
| `Get Bookmark Index` | 获取书签在书签列表中的索引 | `UVPBookmark` |
| `Get Associated Bookmark Actor` | 获取与该书签关联的 Actor | `UVPBookmark` |
| `Get Display Name` | 获取书签的显示名称 | `UVPBookmark` |
| `On Bookmark Activation`（事件） | 当书签被激活或取消激活时触发（在提供者 Actor 上实现） | `IVPBookmarkProvider` |
| `On Bookmark Changed`（事件） | 当书签属性发生变化时触发（在提供者 Actor 上实现） | `IVPBookmarkProvider` |
| `Update Bookmark Spline Mesh Indicator`（事件） | 更新书签的样条线指示器（可用于编辑器可视化） | `IVPBookmarkProvider` |
| `Hide Bookmark Spline Mesh Indicator`（事件） | 隐藏书签的样条线指示器 | `IVPBookmarkProvider` |
| `Generate Bookmark Name`（事件） | 生成书签的名称（可自定义实现） | `IVPBookmarkProvider` |

### 使用示例（蓝图描述）

1. **在蓝图中获取所有书签 Actor**  
   - 调用 `Get All VP Bookmark Actors`（需传入 World Context Object）  
   - 输出 `OutActors` 数组，可遍历并对每个 Actor 执行操作  

2. **创建书签时自动命名**  
   - 在 `IVPBookmarkProvider.GenerateBookmarkName` 事件图表中，调用 `Create VP Bookmark Name` 传入当前 Actor 和格式字符串（如 `"Cam_{number}"`）  
   - 得到 `GeneratedNumber` 和 `GeneratedLetter`，拼接后设置到书签的显示名称中  

3. **激活书签时触发灯光切换**  
   - 在实现了 `IVPBookmarkProvider` 的 Actor（如灯光蓝图）中，重写 `On Bookmark Activation` 事件  
   - 根据 `bActivate` 开启/关闭灯光，或调整颜色  

---

## C++ 用法

### 头文件引入

```cpp
#include "VPBookmark.h"
#include "VPBookmarkBlueprintLibrary.h"
#include "IVPBookmarkProvider.h"
```

### 基本用法

**创建并关联 VP 书签**（通常在编辑器工具或运行时逻辑中）：

```cpp
// 来源：示例代码，基于 API 推导
AActor* TargetActor = ...;
UVPBookmark* Bookmark = NewObject<UVPBookmark>(TargetActor);
Bookmark->CreationContext.CategoryName = FName("Cameras");
Bookmark->CreationContext.DisplayName = TEXT("Main Cam");
Bookmark->CachedViewportData.JumpToOffsetLocation = FVector(100, 200, 300);
Bookmark->CachedViewportData.LookRotation = FRotator(0, -45, 0);

// 关联 Actor
Bookmark->OwnedActor = TargetActor;
// 标记为活跃（触发 IVPBookmarkProvider::OnBookmarkActivation）
Bookmark->SetActive(true);
```

**查找已有书签**：

```cpp
// 来源：VPBookmarkBlueprintLibrary.h
AActor* Actor = ...;
UVPBookmark* Bookmark = UVPBookmarkBlueprintLibrary::FindVPBookmark(Actor);
if (Bookmark)
{
    FText DisplayName = Bookmark->GetDisplayName();
    int32 Index = Bookmark->GetBookmarkIndex();
}
```

**获取世界中所有书签**：

```cpp
// 来源：VPBookmarkBlueprintLibrary.h
UObject* WorldContext = GetWorld();
TArray<AActor*> Actors;
TArray<UVPBookmark*> Bookmarks;
UVPBookmarkBlueprintLibrary::GetAllVPBookmarkActors(WorldContext, Actors);
UVPBookmarkBlueprintLibrary::GetAllVPBookmark(WorldContext, Bookmarks);
```

**实现书签提供者接口**：

```cpp
// 来源：IVPBookmarkProvider.h
class AMyCameraActor : public AActor, public IVPBookmarkProvider
{
public:
    virtual void OnBookmarkActivation_Implementation(UVPBookmark* Bookmark, bool bActivate) override
    {
        if (bActivate)
        {
            // 跳转到书签位置（通常由外部系统处理）
        }
    }

    virtual void OnBookmarkChanged_Implementation(UVPBookmark* Bookmark) override
    {
        // 书签属性变化时更新自身状态
    }

    virtual void UpdateBookmarkSplineMeshIndicator_Implementation() override { /* ... */ }
    virtual void HideBookmarkSplineMeshIndicator_Implementation() override { /* ... */ }
    virtual void GenerateBookmarkName_Implementation() override { /* ... */ }
};
```

### 进阶用法

**借助生命周期委托监听书签创建/销毁**：

```cpp
// 来源：VPBookmarkLifecycleDelegates.h
#include "VPBookmarkLifecycleDelegates.h"

void RegisterDelegates()
{
    FVPBookmarkLifecycleDelegates::GetOnBookmarkCreated().AddLambda([](UVPBookmark* Bookmark)
    {
        UE_LOG(LogVPBookmark, Log, TEXT("Bookmark created: %s"), *Bookmark->GetDisplayName().ToString());
    });
    FVPBookmarkLifecycleDelegates::GetOnBookmarkDestroyed().AddLambda([](UVPBookmark* Bookmark)
    {
        UE_LOG(LogVPBookmark, Log, TEXT("Bookmark destroyed: %s"), *Bookmark->GetDisplayName().ToString());
    });
}
```

**编辑器中创建 VP 书签（配合视口跳转）**：

VP 书签的 `CachedViewportData` 结构包含跳转所需的视角信息。在编辑器工具中，可在激活时读取该数据并设置编辑器视口相机：

```cpp
// 伪代码，实际需访问 GEditor->GetActiveViewport()
void JumpToBookmark(UVPBookmark* Bookmark)
{
    const FVPBookmarkViewportData& Data = Bookmark->CachedViewportData;
    // 设置视口位置：Data.JumpToOffsetLocation
    // 设置视口旋转：Data.LookRotation
    // 设置正交缩放：Data.OrthoZoom
}
```

---

## Demo 示例

以下是一个最小可编译的 C++ 示例，演示如何创建 VP 书签并与 Actor 关联。

**MyBookmarkActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IVPBookmarkProvider.h"
#include "MyBookmarkActor.generated.h"

UCLASS()
class AMYBOOKMARKACTOR : public AActor, public IVPBookmarkProvider
{
    GENERATED_BODY()

public:
    // 实现 IVPBookmarkProvider 接口
    virtual void OnBookmarkActivation_Implementation(UVPBookmark* Bookmark, bool bActivate) override;
    virtual void OnBookmarkChanged_Implementation(UVPBookmark* Bookmark) override;
    virtual void GenerateBookmarkName_Implementation() override;
};
```

**MyBookmarkActor.cpp**
```cpp
#include "MyBookmarkActor.h"
#include "VPBookmark.h"
#include "VPBookmarkBlueprintLibrary.h"

void AMYBOOKMARKACTOR::OnBookmarkActivation_Implementation(UVPBookmark* Bookmark, bool bActivate)
{
    // 示例：激活时打印信息
    UE_LOG(LogTemp, Log, TEXT("Bookmark %s activated: %s"), *Bookmark->GetDisplayName().ToString(), bActivate ? TEXT("true") : TEXT("false"));
}

void AMYBOOKMARKACTOR::OnBookmarkChanged_Implementation(UVPBookmark* Bookmark)
{
    // 书签属性变化时，更新自己的状态
}

void AMYBOOKMARKACTOR::GenerateBookmarkName_Implementation()
{
    // 使用工具库自动生成名称
    FString Number, Letter;
    UVPBookmarkBlueprintLibrary::CreateVPBookmarkName(this, TEXT("Bmk_{number}"), Number, Letter);
    // 设置到书签的 CreationContext.DisplayName（实际需通过其他方式设置）
}
```

**如何创建书签并关联（在某个 Actor 或 GameMode 中）**：

```cpp
// 在世界中生成 MyBookmarkActor
AMyBookmarkActor* MyActor = GetWorld()->SpawnActor<AMyBookmarkActor>(...);

// 创建 VP 书签对象
UVPBookmark* NewBookmark = NewObject<UVPBookmark>(MyActor);
NewBookmark->CreationContext.CategoryName = FName("Cameras");
NewBookmark->CreationContext.DisplayName = TEXT("MyCameraBookmark");
NewBookmark->CachedViewportData.JumpToOffsetLocation = FVector(0, 0, 200);
NewBookmark->CachedViewportData.LookRotation = FRotator(0, 0, 0);
NewBookmark->OwnedActor = MyActor;

// 激活书签（会触发 OnBookmarkActivation）
NewBookmark->SetActive(true);
```

---

## 模块依赖

从 `VPBookmark.Build.cs` 推断（无特殊依赖）：

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅标准 Core/Engine/Slate 等 |

---

## 维护状态

### 近期更新

- 2025-10-03 e6b66964 — 修复媒体输出提供者的全屏控件问题（未直接影响 VPBookmark）  
- 2025-09-25 4b556c0e — VPUtilities OSC 服务器允许指定地址覆盖（未直接影响 VPBookmark）  
- 2025-09-23 66f6004f — ViewportInteraction 模块废弃（与 VR Editor 一起）  
- 2025-09-10 cb5faa0b — VR Editor 模式废弃，关联类被标记弃用（VPBookmark 不受影响）  
- 2025-08-27 551d3a5b — 修复 BugHawk 和 CIS 弃用警告（模块创建时初始化）  

### 维护评价

- **创建时间**：2025-08-27，距今约 2 个月，属于全新实验性模块  
- **近期更新**：主要是周边模块的修复和废弃标记，VPBookmark 核心 API 未发生变动  
- **活跃度**：作为实验性插件，仍在维护中（最近一次更新在 2025-10-03）  
- **已知问题**：无（新模块，无公开缺陷报告）  
- **推荐使用**：✅ 推荐在虚拟制作项目中使用；但注意是实验性，API 可能在未来版本调整  

---

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities)  
- [VPBookmark 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities/Source/VPBookmark/Public/VPBookmark.h)  
- [VPBookmarkBlueprintLibrary](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities/Source/VPBookmark/Public/VPBookmarkBlueprintLibrary.h)  
- [IVPBookmarkProvider](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities/Source/VPBookmark/Public/IVPBookmarkProvider.h)  
- [VPBookmarkLifecycleDelegates](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities/Source/VPBookmark/Public/VPBookmarkLifecycleDelegates.h)