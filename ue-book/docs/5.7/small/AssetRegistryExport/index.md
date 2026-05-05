# Asset Registry Export

> Converts a given asset registry to a SQLite/CSV database. Each AssetClass gets its own table with the corresponding tags for the class as columns.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AssetRegistryExport (Editor) |
| 创建时间 | 2022-02-24 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/AssetRegistryExport) | |

## 用途

这是一个 **Commandlet 工具**，用于将 UE5 的 Asset Registry（资产注册表）二进制文件导出为可查询的 SQLite 数据库或 CSV 文件。

Asset Registry 是 UE 记录所有资产元数据的内部数据库（类名、路径、Tag 值、依赖关系等），但它是一个二进制格式，无法直接用 SQL 或 Excel 查询。这个 plugin 的存在价值就是：**把不可读的二进制资产注册表变成可以用通用工具分析的结构化数据**。

核心功能：
- 读取打包后的 `AssetRegistry.bin` 文件
- 为每个资产类（如 `Texture2D`、`StaticMesh`）创建独立的表，该类的 Tag 作为列
- 同时维护一个全局 `Assets` 表，包含所有资产及其压缩大小信息
- 可选：分析 Primary Asset 的依赖关系树，输出依赖和大小 CSV

## 使用场景

- **包体分析**：打包后想了解哪些资产占了多少空间 → 导出为 SQLite，用 DB Browser 查询
- **资产盘点**：需要知道项目里有多少 Texture2D、它们的分辨率分布 → 按类查表
- **依赖分析**：想知道某个 Game Feature Data 依赖了哪些资源、有多少是独有的 → 用 `-ListDependencies`
- **CI/CD 集成**：在构建管线中自动导出资产清单，用于审计或报告

## 命令行用法

这是一个 **Commandlet**，不是蓝图可调用的节点。通过命令行启动：

```bash
UnrealEditor-Cmd.exe <ProjectName> -run=AssetRegistryExport <参数>
```

### 参数说明

| 参数 | 说明 |
|---|---|
| `-Input=<path>` | 输入的 AssetRegistry 文件路径（**必填**） |
| `-Output=<path>` | 输出 SQLite 数据库文件路径（与 `-CSV` 二选一） |
| `-CSV=<path>` | 输出 CSV 文件的目录路径（与 `-Output` 二选一）。**注意：会生成大量文件** |
| `-ListDependencies=typea,typeb` | 逗号分隔的 Primary Asset 类型列表，输出依赖关系信息 |
| `-IncludeSharedWithDependencies` | 在依赖列表中也包含共享依赖（标记为 "Shared" 根） |
| `-FilterToClass=<classname>` | 只导出指定类的表（减小数据库体积）。例如 `-FilterToClass="/Script/Engine.Texture2D"` |

### 基本用法：导出为 SQLite

```bash
# 将打包产物的 AssetRegistry 导出为 SQLite 数据库
UnrealEditor-Cmd.exe MyProject -run=AssetRegistryExport \
  -Input="MyProject/Metadata/AssetRegistry.bin" \
  -Output="D:/Output/AssetRegistry.db"
```

### 基本用法：导出为 CSV

```bash
# 导出为 CSV 文件（会在指定目录下生成大量文件）
UnrealEditor-Cmd.exe MyProject -run=AssetRegistryExport \
  -Input="MyProject/Metadata/AssetRegistry.bin" \
  -CSV="D:/Output/CSV/"
```

### 进阶用法：依赖分析

```bash
# 分析 GameFeature 和 PrimaryAssetLabel 类型的依赖关系
UnrealEditor-Cmd.exe MyProject -run=AssetRegistryExport \
  -Input="MyProject/Metadata/AssetRegistry.bin" \
  -CSV="D:/Output/CSV/" \
  -ListDependencies=/Script/GameFeatures.GameFeatureData,/Script/Engine.PrimaryAssetLabel \
  -IncludeSharedWithDependencies
```

> **注意**：`-ListDependencies` 需要以生成该 AssetRegistry 的同一项目的 Commandlet 方式运行，因为它需要访问项目的类层次结构。

### 进阶用法：按类过滤

```bash
# 只导出 Texture2D 相关的数据，减小输出体积
UnrealEditor-Cmd.exe MyProject -run=AssetRegistryExport \
  -Input="MyProject/Metadata/AssetRegistry.bin" \
  -Output="D:/Output/Textures.db" \
  -FilterToClass="/Script/Engine.Texture2D"
```

## 输出格式

### SQLite 输出结构

导出的 SQLite 数据库包含：

- **`Assets` 全局表**：所有资产，列包括 `Name`, `Class`, `Path`, `Stage_ChunkCompressedSize`, `Stage_ChunkSize`, `Stage_ChunkOptionalSize`, `Stage_ChunkStreamingSize`
- **每类一个表**（如 `Engine_Texture2DAssets`）：包含该类特有的 Tag 作为列。类名中的非字母数字字符会被替换为 `_`

### CSV 输出结构

- `Assets.csv` — 全局资产列表
- `Classes/<ClassName>Assets.csv` — 每类一个文件
- `ListedDependencies.csv` — 依赖详情（使用 `-ListDependencies` 时）
- `SizeDependencies.csv` — 依赖大小汇总（使用 `-ListDependencies` 时）

### 依赖分析 CSV 列说明

`ListedDependencies.csv` 的列：

| 列名 | 说明 |
|---|---|
| `RootPrimaryAsset` | 依赖的根资产（或 "Unassigned" / "Shared"） |
| `Name` | 包名 |
| `Class` | 资产类路径 |
| `RootClass` | 向上追溯到的根类（停在 Object/BlueprintCore/DataAsset 等通用类之前） |
| `Stage_ChunkCompressedSize` | 压缩大小（字节） |

`SizeDependencies.csv` 的列：

| 列名 | 说明 |
|---|---|
| `RootPrimaryAsset` | 根资产名 |
| `AllDependenciesCompressedBytes` | 所有依赖的总压缩大小 |
| `UniqueDependenciesCompressedBytes` | 仅该根独有的依赖的压缩大小 |

## 蓝图用法

本 plugin 不提供任何蓝图节点。它是纯 Commandlet 工具。

## C++ 用法

本 plugin 不提供 C++ API。它的唯一入口是 `UAssetRegistryExportCommandlet::Main()`，通过 Commandlet 框架调用。

### 头文件引入

```cpp
// 如果你需要类似功能，可以参考其内部使用的 API：
#include "AssetRegistry/AssetRegistryState.h"
#include "SQLiteDatabase.h"
```

### 内部实现要点

如果你想在自己的工具中实现类似功能，核心流程是：

```cpp
// 1. 加载 AssetRegistry 二进制文件
FAssetRegistryState AssetRegistry;
FArrayReader SerializedAssetData;
FFileHelper::LoadFileToArray(SerializedAssetData, *AssetRegistryFileName);
FAssetRegistrySerializationOptions Options(UE::AssetRegistry::ESerializationTarget::ForDevelopment);
AssetRegistry.Serialize(SerializedAssetData, Options);

// 2. 遍历所有资产，收集每个类的 Tag
AssetRegistry.EnumerateAllAssets(TSet<FName>(), [&](const FAssetData& AssetData)
{
    // AssetData.AssetClassPath — 资产类
    // AssetData.TagsAndValues — 该资产的所有 Tag
    // AssetData.GetTagValue(FName, Value) — 获取特定 Tag 值
    return true;
});

// 3. 查询依赖关系
TArray<FAssetIdentifier> Dependencies;
AssetRegistry.GetDependencies(FAssetIdentifier(PackageName), Dependencies);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础库 |
| `Engine` | 引擎核心 |
| `CoreUObject` | UObject 系统（私有依赖） |
| `SQLiteCore` | SQLite 数据库访问（私有依赖） |
| `AssetRegistry` | 资产注册表读取（私有依赖） |

### Plugin 依赖

| Plugin | 说明 |
|---|---|
| `SQLiteCore` | 提供 `FSQLiteDatabase` 和 `FSQLitePreparedStatement` |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-05-21 | `269aeb1` | Replaced bool arguments with EFindObjectFlags | 代码现代化：将 `FindObject` 的布尔参数替换为枚举标志 |
| 2025-03-26 | `f4067b3` | Add new chunk size tags to global assets table; Allow filtering to a single class type; Fix CSV column order | **功能更新**：新增 `Stage_ChunkSize`/`Stage_ChunkOptionalSize`/`Stage_ChunkStreamingSize` 列；新增 `-FilterToClass` 参数；修复 CSV 列顺序 bug |
| 2024-10-02 | `abaf97c` | Add quotes around tag names to prevent sql errors | Bug 修复：Tag 名如果恰好是 SQL 关键字会导致错误，加了引号 |

### 维护评价

- **创建时间**：2022 年 2 月，约 4 年历史
- **更新频率**：近 1 年有 3 次提交，包括功能增强和 bug 修复，属于**活跃维护**
- **实用性**：这是一个小而精的工具，功能明确、代码简洁（~970 行），无已知重大问题
- **推荐**：✅ 推荐使用。如果你需要分析打包后的资产注册表，这是官方提供的唯一工具。代码量小，即使有问题也容易自行修改
- **注意**：默认未启用（`EnabledByDefault: false`），需要在插件管理器中手动启用，或在命令行中通过 `-run=` 方式直接调用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/AssetRegistryExport)
- [AssetRegistry 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/AssetRegistryExport/Source/Private)
