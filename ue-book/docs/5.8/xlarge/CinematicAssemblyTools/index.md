# Cinematic Assembly Tools (CAT)

> CAT is a suite of cinematic pipeline tools for shot management and linear content creation

| 属性 | 值 |
|---|---|
| 中文名 | 影视组装工具集 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `CineAssemblyTools` (Runtime), `CineAssemblyToolsEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CinematicAssemblyTools) | |

## 用途

**Cinematic Assembly Tools (CAT)** 是 Epic Games 为 **虚拟制片流程** 开发的一套专用工具集。它旨在解决影视、广告、过场动画等线性内容创作中的 **镜头管理**、**时间线编排** 和 **资产组织** 痛点。

该插件不仅仅是一个编辑器扩展，它提供了一套数据模型（Schema）和蓝图/脚本API，让团队能够以 **项目（Production）** 为单位，系统性地规划和管理复杂的镜头序列，从而提升大型线性内容项目的制作效率。

## 使用场景

- 你正在为一个游戏、电影或广告项目制作一系列过场动画 → 使用 CAT 来规划、创建和管理每一个镜头（Shot）。
- 你的影视团队需要一个结构化的方式来组织数百个镜头及其相关资产（场景、角色、道具） → CAT 提供了生产（Production）和布局（Layout）的层级结构来管理它们。
- 你需要在 Unreal Engine 中进行线性叙事内容的粗剪或精剪 → CAT 的镜头管理和时间线工具可以辅助这一流程。
- 你希望用蓝图或 C++ 脚本程序化地批量创建和修改镜头资产 → CAT 提供了丰富的脚本化 API。

## 蓝图用法

CAT 提供了一套蓝图可调用的函数库，用于程序化地操作其核心数据结构。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Production` | 创建一个全新的生产项目，作为所有镜头和布局的顶层容器。 | `UProductionFunctionLibrary` |
| `Create Cine Shot` | 在指定的布局（Layout）下创建一个新的镜头资产。 | `UProductionFunctionLibrary` |
| `Set Shot Properties` | 设置镜头的各种属性，如时间码、长度、备注等。 | `UProductionFunctionLibrary` |
| `Find Shot` | 根据名称或标签查找项目中的镜头。 | `UProductionFunctionLibrary` |
| `Get Shots In Layout` | 获取某个布局下的所有镜头列表。 | `UProductionFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **创建项目**：首先，使用 `Create Production` 节点并指定项目名称（如 “GameIntro_Cinematic”），返回一个 `UProduction` 对象。
2.  **规划布局**：基于这个 `UProduction` 对象，可以调用类似 `Create Layout` 的函数来创建不同的场景或章节布局。
3.  **添加镜头**：选中一个 `ULayout` 对象，使用 `Create Cine Shot` 节点为其添加镜头。输入镜头名称（如 “SHOT_010”）和基础设置。
4.  **配置镜头**：对返回的 `UCineShot` 对象，使用 `Set Shot Properties` 节点来填充时间码、镜头描述、关联的关卡序列等具体信息。
5.  **批量操作**：可以结合循环（For Loop）和 `Get Shots In Layout` 节点，对一批镜头进行统一的属性修改或导出操作。

## C++ 用法

### 头文件引入

```cpp
#include "ProductionFunctionLibrary.h"
#include "CineShot.h"
#include "Production.h"
```

### 基本用法

通过 `UProductionFunctionLibrary` 的静态函数来操作 CAT 数据。
（示例功能推测自模块结构和蓝图节点）

```cpp
// 创建一个新的生产项目
UProduction* MyProduction = UProductionFunctionLibrary::CreateProduction(TEXT("MyFilmProject"));

// 在项目中创建一个镜头
if (MyProduction)
{
    UCineShot* NewShot = UProductionFunctionLibrary::CreateCineShot(MyProduction, TEXT("SHOT_A1"));
    if (NewShot)
    {
        // 设置镜头属性
        UProductionFunctionLibrary::SetShotProperties(NewShot, /* 时间码参数 */, /* 时长参数 */, /* 备注文本 */);
    }
}

// 查找镜头
UCineShot* FoundShot = UProductionFunctionLibrary::FindShot(MyProduction, TEXT("SHOT_A1"));
```

### 进阶用法

结合 CAT 的数据模型和 UE 的编辑器子系统，可以实现更强大的自动化工作流。

```cpp
// 假设在编辑器工具中，遍历一个布局下的所有镜头并生成报告
ULayout* TargetLayout = /* 获取某个布局 */;
TArray<UCineShot*> AllShots = UProductionFunctionLibrary::GetShotsInLayout(TargetLayout);

for (UCineShot* Shot : AllShots)
{
    UE_LOG(LogTemp, Log, TEXT("Shot: %s, Duration: %.2f sec"), *Shot->GetShotName(), Shot->GetDuration());
    // 这里可以调用更多的 API 来处理镜头，例如导出数据、验证资产完整性等
}
```

## Demo 示例

一个创建生产项目和镜头的最小 C++ 示例。

**MyCinematicActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyCinematicActor.generated.h"

class UProduction;

UCLASS()
class AMyCinematicActor : public AActor
{
    GENERATED_BODY()
public:
    UPROPERTY()
    TObjectPtr<UProduction> MyProject;

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SetupProject();
};
```

**MyCinematicActor.cpp**
```cpp
#include "MyCinematicActor.h"
#include "ProductionFunctionLibrary.h"
#include "CineShot.h"
#include "Production.h"

void AMyCinematicActor::SetupProject()
{
    MyProject = UProductionFunctionLibrary::CreateProduction(TEXT("DemoProject"));
    if (MyProject)
    {
        UCineShot* Shot1 = UProductionFunctionLibrary::CreateCineShot(MyProject, TEXT("SHOT_001"));
        if (Shot1)
        {
            // 可以在这里进一步设置镜头属性
            UE_LOG(LogTemp, Warning, TEXT("Created shot: %s"), *Shot1->GetShotName());
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieSceneTools` | 核心依赖。Cinematic Assembly Tools 的镜头数据与 UE 的电影场景（Movie Scene）系统深度集成，用于管理时间线、轨道和序列。 |
| `CinematicAssemblyToolsRuntime` | 提供运行时所需的核心数据类（如 UProduction, UCineShot）。被其他模块依赖。 |

（注意：`CineAssemblyToolsEditor` 模块还依赖一系列编辑器和 Slate 相关模块，如 `ToolMenus`, `EditorFramework`, `AssetRegistry` 等，用于构建编辑器界面和资产导入/导出功能。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `534c9605` | ShotManagement: Suppress warnings in output log when a CineAssemblySchema has no thumbnail brush ass | 当 Schema 缺少缩略图时，抑制输出日志中的警告信息。 |
| 2026-05-14 | `85850dc9` | ShotManagement: Add missing scripting API functions | 补充了缺失的脚本化 API 函数。 |
| 2026-05-14 | `1d99acc3` | ShotManagement: Move ProductionFunctionLibrary.h into Public folder and add API exports | 将关键头文件移至 Public 文件夹并添加 API 导出宏，改善模块的外部可访问性。 |
| 2026-05-14 | `c11b4fd1` | ShotManagement: Add missing Cinematic Assembly Tools scripting API | 进一步补充了插件的脚本化 API。 |
| 2026-05-14 | `d1ca5718` | ShotManagement: Remove non-ASCII characters from plugin files | 清理了源文件中的非 ASCII 字符，提升兼容性。 |

### 维护评价

**维护状态：活跃开发中。**

- **创建时间**：插件于 **2025年4月** 创建，非常年轻（约1年）。
- **近期活动**：在 **2026年5月** 有多次密集提交，内容集中于 **功能增强**（补充脚本API）和 **代码质量改进**（调整文件结构、清理字符）。这表明插件正处于功能完善和稳定化阶段。
- **是否推荐**：**推荐在实验性或原型项目中尝试使用**。该插件是 Epic 官方为虚拟制片打造的工具，方向明确且正在积极开发。但由于标记为**实验性（IsExperimentalVersion）**，其 API 和功能未来可能发生变化，不建议在需要长期稳定维护的生产环境中作为核心依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CinematicAssemblyTools)
- 测试用例路径（推测）：`Engine/Plugins/VirtualProduction/CinematicAssemblyTools/Tests/` （此插件文档未直接提供测试路径，但遵循 UE 惯例，测试通常位于 `Tests/` 子目录下）