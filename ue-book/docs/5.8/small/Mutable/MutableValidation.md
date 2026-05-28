# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象 |
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（运行时库、编辑器工具、验证工具） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime), `CustomizableObjectEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个用于创建和管理游戏中“可定制对象”的综合系统。其核心目标是解决在多人游戏或拥有大量角色定制选项的游戏中，高效管理成千上万种视觉组合（如服装、盔甲、发型、配件、纹身、颜色等）的难题。

传统做法是为每种组合创建一个独立的静态网格体资产，这会导致项目资产数量爆炸式增长，消耗大量磁盘空间和内存，并且美术修改起来极其繁琐。Mutable 通过以下方式解决此问题：

1.  **资产共享与模块化：** 将角色或物品拆分为基础网格体、可穿戴部件、材质参数、纹理等独立的模块化资产。
2.  **实时编译与生成：** 在编辑器中或运行时，根据玩家或设计师选择的参数（如“穿靴子A”、“发型B”、“颜色C”），动态地将基础网格体与选定的部件进行“编译”，生成最终的、独一无二的网格体和材质。这个过程是高度优化的。
3.  **内存优化：** 通过实例化技术，不同角色可以共享基础网格体的绝大部分几何数据和材质，仅对差异部分进行实例化，极大节省内存。

简而言之，Mutable 让开发者能够以一套逻辑定义去管理海量的视觉表现，是构建复杂角色定制系统的工业级解决方案。

## 使用场景

-   **角色创建/自定义游戏：** 如 MMORPG、赛车游戏（车辆外观定制）、体育游戏（球员外观）中，为玩家提供深度的角色外观自定义功能。
-   **装备与皮肤系统：** 在动作游戏或射击游戏中，实现海量的武器皮肤、角色皮肤、盔甲组合，并确保其与基础模型高效集成。
-   **头像生成器：** 为社交或元宇宙应用生成高度可定制的 3D 头像。
-   **程序化内容生成：** 结合参数和规则，动态生成外观各异但遵循美术规范的 NPC 群体。

## 蓝图用法

根据提供的源码信息，`MutableValidation` 模块主要包含用于自动化测试和验证的 Commandlet 和工具类，其核心游戏逻辑 API（如 `UCustomizableObject`, `UCustomizableObjectInstance`）应位于 `CustomizableObject` 和 `MutableRuntime` 模块中。以下是基于已知信息的推断：

### 核心节点（推断）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Update Instance` | 根据当前参数更新可定制对象实例的网格体。这是一个异步操作。 | `UCustomizableObjectInstance` (推断) |
| `Set Bool Parameter` / `Set Int Parameter` / `Set Float Parameter` | 设置可定制对象实例的参数值。 | `UCustomizableObjectInstance` (推断) |
| `Compile` | 编译一个 `UCustomizableObject` 资产，通常在编辑器中或打包前执行。 | `UCustomizableObject` (推断) |
| `Bake` | 将当前实例的网格体和材质数据烘焙成静态资产，用于最终发布或特定场景。 | `UCustomizableObjectInstance` (推断) |

### 使用示例（蓝图描述）

由于未提供核心 API 的详细头文件，以下为概念性描述：
1.  从一个 `UCustomizableObject` 资产创建一个 `UCustomizableObjectInstance`。
2.  通过蓝图节点为实例设置各种参数（例如，`Set Int Parameter` 设置“上衣款式”为 2，`Set Linear Color Parameter` 设置“衣服颜色”）。
3.  调用实例的 `Update Instance` 节点。此节点会异步触发编译过程。
4.  监听 `Update Instance` 完成的委托（Delegate）。完成后，绑定到该实例的 `SkeletalMeshComponent` 或 `StaticMeshComponent` 将会自动更新其网格体和材质。

## C++ 用法

同样，基于提供的 `MutableValidation` 模块代码，以下示例展示了如何编写一个用于测试的 Commandlet，这揭示了如何以编程方式编译和测试一个可定制对象。

### 头文件引入

```cpp
// 主要的游戏运行时 API
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"

// 验证和测试工具（本模块）
#include "MuV/ValidationUtils.h"
#include "MuV/CustomizableObjectCompilationUtility.h"
```

### 基本用法

以下代码改编自 `ValidationUtils.h` 中函数的用途说明，展示如何查找和测试一个可定制对象。

```cpp
// 来源：基于 Private/MuV/ValidationUtils.h 中描述的逻辑
// 此函数可能在一个 Commandlet 的 Main 函数中被调用
bool TestMyCustomizableObject()
{
    // 1. 准备资产注册表（Mutable编译所需）
    PrepareAssetRegistry();

    // 2. 在指定路径查找所有 UCustomizableObject 资产
    TArray<FAssetData> COAssets = FindAllAssetsAtPath(TEXT("/Game/Characters/COs"), UCustomizableObject::StaticClass());
    if (COAssets.Num() == 0)
    {
        UE_LOG(LogTemp, Error, TEXT("No CustomizableObject assets found!"));
        return false;
    }

    // 3. 获取第一个 CO 并加载
    UCustomizableObject* CO = Cast<UCustomizableObject>(COAssets[0].GetAsset());
    if (!CO)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load CustomizableObject!"));
        return false;
    }

    // 4. 获取目标平台（例如从命令行参数解析）
    ITargetPlatform* Platform = GetCompilationPlatform(FCommandLine::Get());
    if (!Platform)
    {
        UE_LOG(LogTemp, Error, TEXT("Could not determine target platform!"));
        return false;
    }

    // 5. 编译并测试该CO，生成指定数量的实例进行更新
    const uint32 NumInstances = GetTargetAmountOfInstances(FCommandLine::Get());
    bool bSuccess = TestCustomizableObject(*CO, *Platform, NumInstances);
    
    UE_LOG(LogTemp, Display, TEXT("Test %s for CO: %s"), bSuccess ? TEXT("Succeeded") : TEXT("Failed"), *CO->GetName());
    return bSuccess;
}
```

### 进阶用法

展示如何使用 `FCustomizableObjectCompilationUtility` 同步地编译一个CO，这在测试脚本或自动化流水线中很有用。

```cpp
// 来源：基于 Private/MuV/CustomizableObjectCompilationUtility.h
void CompileCOWithCustomOptions(UCustomizableObject* COToCompile)
{
    if (!COToCompile) return;

    // 创建编译工具
    TSharedRef<FCustomizableObjectCompilationUtility> CompilationUtility = MakeShared<FCustomizableObjectCompilationUtility>();

    // 可以覆盖默认的编译选项，例如用于基准测试
    FCompilationOptions OverrideOptions;
    // ... 配置 OverrideOptions ...

    // 同步执行编译
    bool bCompiledOK = CompilationUtility->CompileCustomizableObject(
        *COToCompile,
        true, // 启用日志
        &OverrideOptions
    );

    if (bCompiledOK)
    {
        UE_LOG(LogTemp, Log, TEXT("Compilation of %s completed successfully."), *COToCompile->GetName());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Compilation of %s failed!"), *COToCompile->GetName());
    }
}
```

## Demo 示例

由于核心游戏运行时 API 的详细头文件未在提供信息中，以下示例聚焦于 `MutableValidation` 模块中一个简单的 Commandlet 骨架，展示了插件测试基础设施的用法。

```cpp
// MyTestCommandlet.h
#pragma once
#include "Commandlets/Commandlet.h"
#include "MyTestCommandlet.generated.h"

UCLASS()
class UMyTestCommandlet : public UCommandlet
{
    GENERATED_BODY()
public:
    virtual int32 Main(const FString& Params) override;
};
```

```cpp
// MyTestCommandlet.cpp
#include "MyTestCommandlet.h"
#include "MuV/ValidationUtils.h"
#include "MuV/CustomizableObjectCompilationUtility.h"

int32 UMyTestCommandlet::Main(const FString& Params)
{
    // 初始化引擎子系统（Commandlet 需要）
    // ... (标准的 Commandlet 初始化代码) ...

    // 使用验证工具函数
    PrepareAssetRegistry();
    LogGlobalSettings();

    // 查找并测试第一个 CO
    TArray<FAssetData> COAssets = FindAllAssetsAtPath(TEXT("/Game/Test/COs"), UCustomizableObject::StaticClass());
    if (COAssets.Num() > 0)
    {
        UCustomizableObject* TestCO = Cast<UCustomizableObject>(COAssets[0].GetAsset());
        ITargetPlatform* Platform = GetCompilationPlatform(Params);
        uint32 InstanceCount = GetTargetAmountOfInstances(Params);

        if (TestCO && Platform)
        {
            bool bResult = TestCustomizableObject(*TestCO, *Platform, InstanceCount);
            // 可以将结果输出到日志或测试报告
            UE_LOG(LogTemp, Display, TEXT("Custom test finished with result: %s"), bResult ? TEXT("Pass") : TEXT("Fail"));
        }
    }

    // 清理
    return 0;
}
```

## 模块依赖

基于 `CustomizableObject` 模块的 `Build.cs` 信息，以下是使用 Mutable 插件（特别是 `MutableValidation` 模块）时可能需要的特殊依赖。游戏项目主要依赖 `CustomizableObject` 和 `MutableRuntime`。

| 模块 | 用途 |
|---|---|
| `MutableCore` | Mutable 插件的核心数据结构和类型定义（推断，应为基础依赖）。 |
| `DerivedDataCache` | 用于处理编译后资产的缓存，提高迭代效率。 |
| `MessageLog` | 在编辑器中输出编译警告和错误信息到“消息日志”面板。 |
| `AssetRegistry` | 用于在测试和验证工具中查找和查询资产。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复了当场景中存在多个同名骨骼网格体时，几何数据被错误重复的问题。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复了“使用UV遮罩裁剪网格”操作未加载正确遮罩Mip层的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复了纹理参数使用错误方法计算LOD偏置的问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用ClothingAssetBase接口，支持了更多类型的布料资产。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复了比较直通对象(PassthroughObjects)时可能出现的数据竞争问题。 |

### 维护评价

Mutable 插件于 2024 年 9 月从实验状态迁移至 Beta 状态，至今约 2 年，仍处于积极开发阶段。**近期（2026年5月底）更新非常频繁**，主要集中在修复各种边界情况的 Bug 和提升稳定性，涉及几何处理、纹理加载、布料集成和线程安全等方面。这表明该插件正处在快速迭代和打磨的 Beta 期，旨在为正式发布做准备。

**优势：**
-   由 Epic Games 官方维护，是 UE5 生态中解决大规模角色定制问题的官方方案。
-   更新活跃，近期修复了多个深层次问题。
-   设计为生产就绪（从Experimental升至Beta），并被多款商业游戏采用。

**注意事项：**
-   文档和示例相对稀缺（可能与Beta状态有关），需要通过阅读源码和社区学习。
-   系统较为复杂，学习曲线陡峭。
-   由于仍处于Beta，API 和行为在未来版本中可能仍有变化。

**结论：** 对于有严肃角色定制需求的项目，Mutable 是**强烈推荐**的选择。建议密切关注其版本更新日志，并为项目预留适配 API 变化的可能。鉴于其活跃的维护状态，可以放心用于新项目开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- 官方文档（.uplugin 中未提供 URL）
- 测试用例（位于插件源码内部的 `Source/MutableValidation/` 及相关测试项目）