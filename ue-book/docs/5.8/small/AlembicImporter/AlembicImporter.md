# Alembic Importer

> Support importing Alembic files

| 属性 | 值 |
|---|---|
| 中文名 | Alembic 导入器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicImporter` (Editor), `AlembicLibrary` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter) | |

## 用途

本插件用于导入 Alembic (.abc) 文件。Alembic 是影视和游戏行业中广泛使用的开放标准格式，用于在不同数字内容创建（DCC）工具（如 Houdini, Maya, Blender）与游戏引擎之间交换复杂的几何体和动画数据。

插件解决了将 DCC 软件中生成的复杂模拟动画（如流体、布料、刚体）或角色动画导入到 Unreal Engine 中的问题。它能够解析 Alembic 文件中的网格体（PolyMesh）数据，并将其导入为 UE5 中的静态网格体（Static Mesh）、几何缓存（Geometry Cache）或骨骼网格体（Skeletal Mesh）资产，从而保留动画的时间轴信息。

## 使用场景

- 你从 **Houdini** 导出了复杂的流体或刚体模拟动画，希望将其作为动画几何体在 UE5 中回放。
- 你从 **Maya** 或 **Blender** 导出了角色动画或布料模拟，希望导入到 UE5 中进行进一步编辑或使用。
- 你需要导入**带有时间轴的连续几何体变化**，例如变形目标（Morph Target）序列或完整的网格体动画。
- 你需要**重新导入**已导入的 Alembic 资产以更新内容，而不希望丢失在引擎内已进行的材质分配或其他设置。

## 蓝图用法

该插件的核心功能（文件导入和资产创建）主要通过编辑器界面（如“导入”按钮或右键菜单）触发，而非通过蓝图节点。`UAlembicImportFactory` 是编辑器工厂类，其函数（如 `FactoryCreateFile`）由编辑器在导入过程中自动调用。

用户通常通过以下方式交互：
1.  在内容浏览器中右键，选择“导入到此处”。
2.  选择 `.abc` 文件。
3.  在弹出的 `SAlembicImportOptions` 窗口中配置导入选项（如选择导入为 StaticMesh、GeometryCache 还是 SkeletalMesh，选择要导入的 Track 等）。
4.  点击“导入”。

该插件没有专门为蓝图运行时（Runtime）暴露可调用的函数节点。

## C++ 用法

### 头文件引入

```cpp
#include "AlembicImportFactory.h"
// 通常还需要包含导入设置类
#include "AbcImportSettings.h"
```

### 基本用法

在编辑器代码中，可以通过工厂类进行程序化导入（虽然通常由编辑器UI触发）。

```cpp
// 假设你已经有了一个 FAbcImporter 实例（通常由工厂内部创建）
// 这里演示如何从工厂类的角度调用导入函数。
// 来源文件: Engine/Plugins/Importers/AlembicImporter/Source/AlembicImporter/Classes/AlembicImportFactory.h

// 创建工厂实例
UAlembicImportFactory* Factory = NewObject<UAlembicImportFactory>();

// 设置导入参数（通常通过 UI 或导入数据填充）
// Factory->ImportSettings = ... ;
// Factory->bShowOption = false; // 如果不希望弹出选项窗口

// 准备导入参数
UClass* ClassToCreate = UStaticMesh::StaticClass(); // 或 UGeometryCache, USkeletalMesh
UObject* ParentPackage = CreatePackage(TEXT("/Game/ImportedAssets"));
FName AssetName = TEXT("MyAlembicAsset");
EObjectFlags Flags = RF_Public | RF_Standalone;
FString FilePath = TEXT("/path/to/your/file.abc");
FFeedbackContext* Warn = GWarn;
bool bOperationCanceled = false;

// 调用工厂的创建文件函数
UObject* ImportedObject = Factory->FactoryCreateFile(
    ClassToCreate,
    ParentPackage,
    AssetName,
    Flags,
    FilePath,
    nullptr, // Parms
    Warn,
    bOperationCanceled
);
```

### 进阶用法

重新导入（Reimport）已存在的资产是常见需求，该功能由 `FReimportHandler` 接口支持。

```cpp
// 假设你已经有一个之前导入的 UStaticMesh 指针
// 来源文件: Engine/Plugins/Importers/AlembicImporter/Source/AlembicImporter/Classes/AlembicImportFactory.h

UStaticMesh* ExistingMesh = ... ; // 之前导入的网格体
UAlembicImportFactory* Factory = NewObject<UAlembicImportFactory>();

// 检查是否可以重新导入
TArray<FString> OutFilenames;
if (Factory->CanReimport(ExistingMesh, OutFilenames))
{
    // 执行重新导入
    EReimportResult::Type Result = Factory->Reimport(ExistingMesh);
    if (Result == EReimportResult::Succeeded)
    {
        UE_LOG(LogTemp, Log, TEXT("Alembic 文件重新导入成功。"));
    }
}
```

## Demo 示例

以下是一个简单的编辑器命令示例，演示如何使用 Alembic 工厂进行导入。此示例用于说明原理，实际项目中通常直接使用编辑器的导入UI。

**MyAlembicImportCommandlet.h**
```cpp
#pragma once
#include "Commandlets/Commandlet.h"
#include "MyAlembicImportCommandlet.generated.h"

UCLASS()
class UMyAlembicImportCommandlet : public UCommandlet
{
    GENERATED_BODY()
public:
    virtual int32 Main(const FString& Params) override;
};
```

**MyAlembicImportCommandlet.cpp**
```cpp
#include "MyAlembicImportCommandlet.h"
#include "AlembicImportFactory.h"
#include "AssetRegistry/AssetRegistryModule.h"

int32 UMyAlembicImportCommandlet::Main(const FString& Params)
{
    // 解析参数获取文件路径
    TArray<FString> Tokens;
    TArray<FString> Switches;
    ParseCommandLine(*Params, Tokens, Switches);

    if (Tokens.Num() < 1)
    {
        UE_LOG(LogTemp, Error, TEXT("请提供要导入的 .abc 文件路径。"));
        return 1;
    }

    const FString AbcFilePath = FPaths::ConvertRelativePathToFull(Tokens[0]);
    if (!FPaths::FileExists(AbcFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("文件不存在: %s"), *AbcFilePath);
        return 1;
    }

    // 创建工厂
    UAlembicImportFactory* Factory = NewObject<UAlembicImportFactory>();
    Factory->bShowOption = false; // 禁用选项窗口

    // 准备导入
    FString AssetName = FPaths::GetBaseFilename(AbcFilePath);
    UPackage* Pkg = CreatePackage(*FString::Printf(TEXT("/Game/ImportedABC/%s"), *AssetName));
    bool bCanceled = false;

    UE_LOG(LogTemp, Log, TEXT("开始导入: %s"), *AbcFilePath);
    UObject* ImportedAsset = Factory->FactoryCreateFile(
        UStaticMesh::StaticClass(), // 尝试导入为静态网格体
        Pkg,
        *AssetName,
        RF_Public | RF_Standalone,
        AbcFilePath,
        nullptr,
        GWarn,
        bCanceled
    );

    if (ImportedAsset)
    {
        UE_LOG(LogTemp, Log, TEXT("导入成功: %s"), *ImportedAsset->GetPathName());
        // 保存资产
        FAssetRegistryModule::AssetCreated(ImportedAsset);
        Pkg->MarkPackageDirty();
        Pkg->SetDirtyFlag(true);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("导入失败。"));
    }

    return ImportedAsset ? 0 : 1;
}
```

## 模块依赖

从 `Build.cs` 文件分析，使用该插件的功能时，你的模块可能需要依赖：

| 模块 | 用途 |
|---|---|
| `AlembicLibrary` | 核心 Alembic 解析和处理库，必须依赖。 |
| `GeometryCache` | 用于创建和操作 `UGeometryCache` 资产。插件依赖它。 |
| `RenderCore` | 涉及渲染数据处理。 |
| `MeshDescription` | 用于构建网格体数据。 |
| `SkeletalMeshDescription` | 用于构建骨骼网格体数据。 |
| `StaticMeshDescription` | 用于构建静态网格体数据。 |

*注：常见的 Core, CoreUObject, Engine, Slate, EditorStyle, UnrealEd 等模块已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了 64 位参数与 32 位格式说明符不匹配的问题，提升了平台兼容性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，是引擎日志系统现代化的一部分。 |
| 2026-02-27 | `8ce7ca27` | AlembicImporter: Fixed import failure when it couldn't retrieve velocities even though those should | 修复了在应该存在速度数据但无法获取时导致的导入失败问题。 |
| 2026-02-25 | `74e86b93` | Alembic Import: Fixed out of bouds access (potentially due to negative times). | 修复了可能由负数时间引起的越界访问错误，增强了稳定性。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了不可达代码错误，属于代码清理和编译兼容性修复。 |

### 维护评价

- **活跃维护**：该插件在 2022 年从实验性状态迁移至正式状态，并且**持续有活跃更新**。最近一次功能性修复发生在 2026 年 4 月，且 2026 年 2 月有多次错误修复。
- **功能稳定**：近期的提交主要集中在**错误修复、平台兼容性改进和引擎基础设施适配**（如日志宏迁移），表明其核心功能已相对稳定，团队致力于保持其健壮性和与最新引擎版本的兼容。
- **依赖关系**：作为 `GeometryCache` 插件的依赖项，它随着引擎核心功能一起维护。
- **推荐使用**：该插件是 UE5 中处理 Alembic 文件的标准且官方的解决方案。鉴于其活跃的维护状态和近期的稳定性修复，**强烈推荐**在需要导入 Alembic 资产时使用。没有证据表明它已被废弃。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter/Tests) *(基于常规结构推断)*