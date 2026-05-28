# GeneSplicer Editor

> GeneSplicer plugin for facial animation

| 属性 | 值 |
|---|---|
| 中文名 | 基因剪接器 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeneSplicerLib` (Runtime), `GeneSplicerLibTest` (Runtime), `GeneSplicerModule` (Runtime), `GeneSplicerEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GeneSplicer) | |

## 用途
`GeneSplicerEditor` 是 `GeneSplicer` 插件的编辑器扩展模块。它的核心职责是为 `GeneSplicer` 插件所使用的特定资产类型（如 `GenePool` 资产和 `RegionAffiliation` 资产）提供在 Unreal Editor 中的创建、导入和管理支持。该模块包含资产工厂（UFactory）和资产类型操作（FAssetTypeActions）类，确保这些定制资产能无缝集成到引擎的编辑器工作流中，例如在内容浏览器中创建、通过拖放导入 `.dna` 格式的文件等。

## 使用场景
- 你正在开发一个需要高质量、程序化驱动面部动画的游戏项目（如大量NPC或可定制角色），并且使用了 `GeneSplicer` 系统。
- 你的美术或技术美术需要将外部的面部动画数据（DNA文件）导入到 Unreal 项目中，并希望像管理其他标准资产一样在编辑器内管理这些数据。
- 你需要通过编辑器的菜单或内容浏览器右键菜单直接创建 `GenePool` 或 `RegionAffiliation` 资产。

## 蓝图用法
本模块 (`GeneSplicerEditor`) 主要提供编辑器的后端支持（资产工厂和操作），不直接暴露 `BlueprintCallable` 函数节点。对 `GeneSplicer` 核心功能的调用和配置通常在运行时 (`GeneSplicerModule`, `GeneSplicerLib`) 或通过其他编辑器工具（如自定义面板、资产编辑器）进行。

## C++ 用法
该模块主要供编辑器内部和插件开发者扩展使用。

### 头文件引入
```cpp
#include "GeneSplicerEditor.h"
```

### 基本用法
`GeneSplicerEditor` 模块的主要功能是注册资产类型。以下是其模块类 `FGeneSplicerEditorModule` 的典型生命周期：

```cpp
// 来自 Public/GeneSplicerEditor.h
void FGeneSplicerEditorModule::StartupModule()
{
    // 注册 GenePool 资产类型操作
    GenePoolAssetTypeActions = MakeShareable(new FGenePoolAssetTypeActions());
    FAssetToolsModule::GetModule().Get().RegisterAssetTypeActions(GenePoolAssetTypeActions.ToSharedRef());
    // 通常还会注册 RegionAffiliation 的资产类型操作
}

void FGeneSplicerEditorModule::ShutdownModule()
{
    // 注销资产类型操作
    if (FAssetToolsModule::IsLoaded())
    {
        FAssetToolsModule::GetModule().Get().UnregisterAssetTypeActions(GenePoolAssetTypeActions.ToSharedRef());
    }
}
```

### 进阶用法
开发者可以继承或参考该模块中定义的工厂类，来创建自定义的资产导入器。例如，`UGenePoolAssetImportFactory` 展示了如何处理 `.dna` 文件导入：

```cpp
// 来自 Public/GenePoolAssetImportFactory.h
UCLASS()
class GENESPLICEREDITOR_API UGenePoolAssetImportFactory : public UFactory
{
    // ...
    virtual bool FactoryCanImport(const FString& Filename) override
    {
        return FPaths::GetExtension(Filename).Equals(TEXT("dna"), ESearchCase::IgnoreCase);
    }
    virtual UObject* FactoryCreateFile(...) override
    {
        // 实际的 DNA 文件解析和 GenePool 资产创建逻辑在此处实现
        // ...
    }
};
```

## Demo 示例
以下示例展示了如何通过 `GeneSplicerEditor` 模块提供的功能，在代码中请求导入一个 DNA 文件（类似编辑器拖放文件到内容浏览器的底层流程）：

```cpp
// MyAssetImporter.h
#pragma once
#include "CoreMinimal.h"

class FMyDnaImporter
{
public:
    static bool ImportDnaToProject(const FString& DnaFilePath, const FString& DestinationPath);
};
```

```cpp
// MyAssetImporter.cpp
#include "MyAssetImporter.h"
#include "GenePoolAssetImportFactory.h"
#include "AssetToolsModule.h"
#include "AssetImportTask.h"

bool FMyDnaImporter::ImportDnaToProject(const FString& DnaFilePath, const FString& DestinationPath)
{
    FAssetToolsModule& AssetToolsModule = FAssetToolsModule::GetModule();
    IAssetTools& AssetTools = AssetToolsModule.Get();

    // 创建导入任务
    UAssetImportTask* ImportTask = NewObject<UAssetImportTask>();
    ImportTask->Filename = DnaFilePath;
    ImportTask->DestinationPath = DestinationPath;
    ImportTask->bSave = true;
    ImportTask->bAutomated = true; // 无UI模式

    // 查找对应的工厂（GeneSplicerEditor模块已注册）
    UFactory* Factory = AssetTools.GetFactoryForImportType(DnaFilePath);
    if (Factory && Factory->IsA<UGenePoolAssetImportFactory>())
    {
        // 使用工厂执行导入
        bool bSuccess = AssetTools.ImportAssetTasks({ ImportTask });
        return bSuccess && !ImportTask->Result.Get()->IsA<UObject>(); // 检查结果
    }
    return false;
}
```

## 模块依赖
本模块 (`GeneSplicerEditor`) 的依赖已在 Build.cs 中声明，但对于使用者（即希望调用其导入功能或在自己的编辑器工具中集成）的模块，通常无需额外依赖特殊模块，因为其核心逻辑通过引擎的 `AssetTools` 模块调用。

| 模块 | 用途 |
|---|---|
| `GeneSplicerLib` | 依赖的核心库，用于 DNA 数据解析和 GenePool 数据结构 |
| `AssetTools` | (引擎模块) 用于执行资产导入和注册资产类型操作 |
| `UnrealEd` | (引擎模块) 编辑器核心，提供 UFactory 基类等 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2f6aa301` | Improve DNA asset load performance and backwards compatible conversion by reducing data copies | 优化 DNA 资产加载性能，通过减少数据拷贝提升向后兼容性转换效率。 |
| 2026-05-12 | `57c5e2c7` | Update DNA and RigLogic to better handle malformed DNA files | 更新 DNA 和 RigLogic 以更好地处理格式错误的 DNA 文件。 |
| 2026-05-12 | `0577289d` | Suppress private module include warnings for test modules (RigLogicLibTest, DNACalibLibTest, DNACali...) | 抑制了测试模块（RigLogicLibTest, DNACalibLibTest 等）的私有模块包含警告。 |
| 2026-04-30 | `82833e51` | Fix data-race on per platform DNAConfig access during serialization | 修复了在序列化期间访问每平台 DNAConfig 时的数据竞争问题。 |
| 2026-04-28 | `0c7a803e` | Implement face-winding conversion in DNA to support arbitrary coordinate systems in UE | 在 DNA 中实现面朝向转换，以支持 UE 中的任意坐标系。 |

### 维护评价
- **活跃维护**：该插件自2024年10月创建以来，保持了持续的更新。最近的提交（2026年5月）集中在**性能优化**和**健壮性提升**（更好的错误文件处理、修复数据竞争），表明开发团队正在积极改进其核心功能和稳定性。
- **推荐使用**：作为 Epic Games 官方维护的面部动画解决方案的一部分，`GeneSplicer` 及其编辑器模块 (`GeneSplicerEditor`) 是生产级工具，适合需要复杂、高质量面部动画的项目使用。建议关注其对 `RigLogic` 插件的依赖。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GeneSplicer)