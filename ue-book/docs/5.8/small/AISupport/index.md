# AISupport

> A simple plugin that makes sure your project loads AIModule and NavigationSystem at runtime

| 属性 | 值 |
|---|---|
| 中文名 | AI支持 |
| 分类 | AI |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AISupportModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-12-27 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/AISupport) | |

## 用途

AISupport 插件本身**不提供任何AI功能**。它的唯一作用是作为一个轻量级的依赖项，确保 `AIModule` 和 `NavigationSystem` 这两个核心AI模块在项目启动时（`PostConfigInit` 阶段）被加载。

它解决的是**模块加载顺序和依赖管理**的问题。当你的项目需要使用AI功能（如行为树、黑板、导航网格等），但又不想在项目的 `.Build.cs` 中直接显式依赖 `AIModule` 和 `NavigationSystem` 时，启用此插件可以保证这些底层模块可用，避免运行时出现模块未加载的错误。

## 使用场景

- 你的项目需要使用虚幻引擎的AI系统（行为树、AI控制器、感知系统等）。
- 你的项目需要使用导航系统（NavMesh、寻路）。
- 你希望以一种“声明式”的方式确保AI基础模块被加载，而不是在代码中手动管理依赖。

## 蓝图用法

无。该插件不包含任何蓝图可调用的函数或属性。

## C++ 用法

### 头文件引入

```cpp
#include "AISupportModule.h"
```

### 基本用法

该插件主要用于模块加载保障，通常无需在代码中直接交互。你可以通过以下方式检查模块是否已加载：

```cpp
// 检查 AISupportModule 是否已加载（通常它会自动加载）
if (IAISupportModule::IsAvailable())
{
    // 模块已加载，意味着 AIModule 和 NavigationSystem 也已加载
    UE_LOG(LogTemp, Log, TEXT("AISupportModule is available. AI and Navigation systems should be loaded."));
}
```

### 进阶用法

由于插件本身无功能，进阶用法主要体现在理解其背后的模块依赖关系。如果你在开发一个需要AI功能的插件或模块，可以在你的 `.Build.cs` 中依赖 `AISupportModule`，从而间接获得对 `AIModule` 和 `NavigationSystem` 的依赖。

```cpp
// 在你的模块的 .Build.cs 文件中
PublicDependencyModuleNames.AddRange(new string[] {
    "AISupportModule" // 通过依赖此模块，间接依赖 AIModule 和 NavigationSystem
});
```

## Demo 示例

一个最小的示例，展示如何在运行时检查 AISupport 模块的状态。

**MyAIChecker.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyAIChecker.generated.h"

UCLASS()
class AMyAIChecker : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};
```

**MyAIChecker.cpp**
```cpp
#include "MyAIChecker.h"
#include "AISupportModule.h"

void AMyAIChecker::BeginPlay()
{
    Super::BeginPlay();

    if (IAISupportModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("AISupportModule is loaded. AI systems are ready."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("AISupportModule is NOT loaded! AI systems may not function."));
    }
}
```

## 模块依赖

该插件的 `Build.cs` 文件会声明对以下模块的依赖，这是其核心功能所在：

| 模块 | 用途 |
|---|---|
| `AIModule` | 虚幻引擎核心AI系统，提供行为树、黑板、AI控制器等 |
| `NavigationSystem` | 虚幻引擎导航系统，提供NavMesh生成、寻路等功能 |

## 维护状态

### 近期更新

```
- 2024-10-22 98a8e0e0 Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes
- 2023-01-13 3c9aacb1 [Engine/Plugins]
- 2023-01-12 2f78497e [Engine/Plugins]
- 2022-10-21 610c4676 Update vendor links for built-in plugins to use secure protocol.
- 2019-12-27 28d3d740 (Integrating from Dev-EngineMerge to Main)
```

### 维护评价

- **创建时间**：2019年12月，已有约5年历史。
- **最近更新频率和内容**：最近一次更新（2024-10-22）是清理废弃的宏，属于代码维护性改动，非功能性更新。之前的更新也多为全局性的代码整理或链接更新。
- **活跃度**：**维护不活跃**。该插件功能极其简单且稳定，自创建后没有进行过功能性增强或重大修改。最近的提交都是跟随引擎整体的代码清理工作。
- **已知问题或限制**：无已知问题。其限制在于它本身不提供任何功能，仅作为依赖加载器。
- **推荐使用**：**推荐**。如果你需要确保AI和导航系统模块在运行时可用，这是一个简单、无副作用且由Epic官方维护的解决方案。尽管不活跃，但其功能稳定，无需频繁更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/AISupport)