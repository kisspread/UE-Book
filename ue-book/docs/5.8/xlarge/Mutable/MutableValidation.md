# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 可变对象插件 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 插件的核心功能是提供一套完整的框架，用于创建和管理运行时可定制的游戏对象。它并非简单的参数修改，而是支持对对象的结构、材质、网格、纹理等进行深度、动态的混合与组合，从而在无需生成大量独立资产的情况下，实现高度个性化和多样化的内容，例如角色外观定制、装备变体、资源优化（LOD与材质合并）等。`MutableValidation` 子模块是该插件的“质量保障”模块，专注于自动化测试、验证和性能基准测试，以确保可定制对象资产在开发和持续集成流程中的正确性与效率。

## 使用场景

- 你的游戏需要玩家深度自定义角色外观（发型、面容、纹身、服装组合）→ 用 Mutable 的运行时和工具链。
- 你需要为大量同类对象（如不同颜色的盔甲、不同材质的武器）生成可优化运行的变体，而非复制整个资产 → 用 Mutable 生成“可定制对象”。
- 你的团队在大型项目中需要自动化验证所有可定制对象的编译和生成功能，以确保 CI/CD 流水线的稳定性 → 用 `MutableValidation` 模块提供的 Commandlet 和资产验证器。

## 蓝图用法

`MutableValidation` 模块主要提供验证和命令行工具，蓝图中直接调用的公开 API 较少。其核心价值在于在编辑器运行和命令行模式下自动执行验证任务。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsCustomizableObjectValid` | 静态函数，编译并检查一个可定制对象的有效性，返回验证结果及错误/警告信息。 | `UAssetValidator_CustomizableObjects` |

### 使用示例（蓝图描述）

在蓝图中，此函数通常用于编辑器工具或数据核查逻辑。你可以通过 `UAssetValidator_CustomizableObjects::IsCustomizableObjectValid` 静态方法，传入一个 `UCustomizableObject` 指针，来同步地触发其编译验证并获取结果。由于是静态函数，你可以直接通过类名调用。结果会通过输出引脚返回 `EDataValidationResult`（`Valid`, `Invalid`, `NotValidated`）以及错误和警告文本数组。

## C++ 用法

本模块主要用于自动化测试和验证，C++ 用法侧重于编写测试用例、执行验证和集成到资产处理流程中。

### 头文件引入

```cpp
#include "MuV/ValidationUtils.h"
#include "MuV/CustomizableObjectCompilationUtility.h"
#include "MuV/CustomizableObjectInstanceUpdateUtility.h"
```

### 基本用法

同步编译一个可定制对象。
(来源: `Private/MuV/CustomizableObjectCompilationUtility.h`)

```cpp
// 假设你已经拥有一个 UCustomizableObject* 的指针
UCustomizableObject* MyCO = ...; 

// 创建编译辅助工具
TSharedRef<FCustomizableObjectCompilationUtility> CompileUtil = MakeShareable(new FCustomizableObjectCompilationUtility());

// 执行同步编译
bool bSuccess = CompileUtil->CompileCustomizableObject(*MyCO, true /* bShouldLogMutableLogs */);
if (bSuccess)
{
    // 编译成功，可以继续进行实例更新等操作
}
```

### 进阶用法

编译对象并同步更新一个实例。
(结合 `FCustomizableObjectCompilationUtility` 和 `FCustomizableObjectInstanceUpdateUtility`)

```cpp
#include "MuV/CustomizableObjectCompilationUtility.h"
#include "MuV/CustomizableObjectInstanceUpdateUtility.h"
#include "MuCO/CustomizableObjectInstance.h"

// 1. 编译 CO
TSharedRef<FCustomizableObjectCompilationUtility> CompileUtil = MakeShareable(new FCustomizableObjectCompilationUtility());
if (CompileUtil->CompileCustomizableObject(*MyCO))
{
    // 2. 创建并配置实例（参数设置等）
    UCustomizableObjectInstance* MyInstance = MyCO->CreateInstance();
    MyInstance->SetIntParameter("HairStyle", 3);
    
    // 3. 同步更新实例（生成网格等）
    TSharedRef<FCustomizableObjectInstanceUpdateUtility> UpdateUtil = MakeShareable(new FCustomizableObjectInstanceUpdateUtility());
    bool bInstanceReady = UpdateUtil->UpdateInstance(*MyInstance);
    
    if (bInstanceReady)
    {
        // 实例已就绪，可以附加到骨骼网格体组件上使用
    }
}
```

## Demo 示例

以下是一个完整的、可在 `UCustomizableObjectValidationCommandlet` 类似的场景中使用的最小验证示例，展示了编译与实例化的核心流程。

```cpp
// MyMutableTest.h
#pragma once
#include "CoreMinimal.h"

class UCustomizableObject;
class UCustomizableObjectInstance;

class FMyMutableTest
{
public:
    /** 执行一个针对指定 CO 的简单编译与实例化测试 */
    static bool RunBasicCOUpdateTest(UCustomizableObject* InCO);
};
```

```cpp
// MyMutableTest.cpp
#include "MyMutableTest.h"
#include "MuV/CustomizableObjectCompilationUtility.h"
#include "MuV/CustomizableObjectInstanceUpdateUtility.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "HAL/PlatformMisc.h"

bool FMyMutableTest::RunBasicCOUpdateTest(UCustomizableObject* InCO)
{
    if (!InCO)
    {
        UE_LOG(LogTemp, Error, TEXT("输入的 CustomizableObject 为空"));
        return false;
    }

    // 1. 编译
    TSharedRef<FCustomizableObjectCompilationUtility> CompileUtil = MakeShareable(new FCustomizableObjectCompilationUtility());
    UE_LOG(LogTemp, Log, TEXT("正在编译可定制对象: %s"), *InCO->GetName());
    if (!CompileUtil->CompileCustomizableObject(*InCO))
    {
        UE_LOG(LogTemp, Error, TEXT("编译失败"));
        return false;
    }

    // 2. 创建实例并更新
    UCustomizableObjectInstance* Instance = InCO->CreateInstance();
    if (!Instance)
    {
        UE_LOG(LogTemp, Error, TEXT("创建实例失败"));
        return false;
    }

    TSharedRef<FCustomizableObjectInstanceUpdateUtility> UpdateUtil = MakeShareable(new FCustomizableObjectInstanceUpdateUtility());
    UE_LOG(LogTemp, Log, TEXT("正在更新实例..."));
    if (!UpdateUtil->UpdateInstance(*Instance))
    {
        UE_LOG(LogTemp, Error, TEXT("更新实例失败"));
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("对象编译和实例更新测试通过。"));
    return true;
}
```

## 模块依赖

从 `MutableValidation` 模块的 `Build.cs` 分析得出。该模块主要用于编辑器和测试环境。

| 模块 | 用途 |
|---|---|
| `DerivedDataCache` | 访问引擎的派生数据缓存系统，与资源编译和缓存紧密相关。 |
| `MessageLog` | 在编辑器中记录和显示验证消息、错误和警告。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复同名骨骼网格体导致的几何体重复问题。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复了UV遮罩剪裁网格操作加载错误Mip等级的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. | 修复纹理参数计算LOD偏差方法错误的问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用ClothingAssetBase接口支持更多服装资产类型。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较PassthroughObjects时可能出现的数据竞争。 |

### 维护评价

- **状态**：**活跃维护**。创建于2024年9月，最近的更新集中在2026年5月底，且都是实质性的Bug修复和功能改进，表明插件正在被积极开发和调试。
- **风险提示**：该插件状态标记为“Beta”（从Experimental迁移），这意味着虽然功能强大且可用于项目，但API和功能未来仍有可能发生破坏性变更。建议在项目中谨慎采用，并关注版本更新说明。
- **推荐**：如果你的项目有深度角色或装备定制需求，Mutable 是目前UE官方提供的最强大的解决方案。`MutableValidation` 模块是保障你大规模使用此插件时资产质量的关键工具，**强烈推荐在CI/CD流程中集成其提供的Commandlet进行自动化验证**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Tests) (MutableTesting 插件，通常位于此路径或插件内的Tests目录)
- (官方文档链接未在.uplugin中提供，建议查阅UE官方文档或社区资源)