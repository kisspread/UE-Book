# CineAssemblyTools（Runtime 模块）

> Runtime 模块，提供核心数据类型：CineAssembly、CineAssemblySchema、CineAssemblyNamingTokens。

## 模块概览

| 属性 | 值 |
|---|---|
| 模块名 | `CineAssemblyTools` |
| 类型 | Runtime |
| 加载阶段 | Default |
| 源文件数 | 7（3 个头文件 + 4 个 cpp 文件） |

### 源文件列表

| 文件 | 说明 |
|---|---|
| `Public/CineAssembly.h` | 核心 Assembly 资产类，继承自 ULevelSequence |
| `Public/CineAssemblySchema.h` | Schema 模板定义类 |
| `Public/CineAssemblyNamingTokens.h` | 命名令牌系统，用于模板化名称解析 |
| `Private/CineAssembly.cpp` | Assembly 实现 |
| `Private/CineAssemblySchema.cpp` | Schema 实现 |
| `Private/CineAssemblyNamingTokens.cpp` | 命名令牌实现 |
| `Private/CineAssemblyToolsModule.cpp` | 模块启动/关闭 |

## 核心类：UCineAssembly

`UCineAssembly` 继承自 `ULevelSequence`，是 CAT 系统的核心资产类型。它将一个 Level Sequence 与以下信息关联：

- **Level**：关联的世界场景
- **Schema**：创建时使用的模板
- **Parent Assembly**：父级 Assembly（支持层级结构）
- **Production**：所属的制作项目
- **Metadata**：自定义元数据（键值对，序列化为 JSON）
- **Sub Assemblies**：自动创建的子序列
- **Data-Only 标记**：标记为 Data-Only 时，打开 Assembly 只显示详情而非 Sequencer

### 关键属性

```cpp
// Assembly 名称，支持命名令牌
FTemplateString AssemblyName;

// 关联的 Level
FSoftObjectPath Level;

// 用户自定义元数据
TMap<FName, FString> InstanceMetadata;

// 备注文本
FString AssemblyNote;

// 父 Assembly 引用
FSoftObjectPath ParentAssembly;

// Production ID 和名称
FGuid Production;
FString ProductionName;

// 子序列模板名称列表
TArray<FTemplateString> SubAssemblyNames;

// 子序列 Section 列表
TArray<TObjectPtr<UMovieSceneSubSection>> SubAssemblies;

// Data-Only 标记
bool bIsDataOnly = false;
```

### 关键方法

#### 生命周期

| 方法 | 说明 |
|---|---|
| `Initialize()` | 初始化 Assembly（调用父类 Initialize） |
| `InitializeFromTemplate(ULevelSequence*)` | 从模板 Level Sequence 初始化，复制 MovieScene 和绑定引用 |
| `SetSchema(UCineAssemblySchema*)` | 设置 Schema，仅在未设置时生效 |
| `CreateSubAssemblies()` | 根据 Schema 创建子序列和文件夹（仅编辑器） |

#### 蓝图可调用方法

| 方法 | 签名 | 说明 |
|---|---|---|
| `GetLevel` | `TSoftObjectPtr<UWorld> GetLevel()` | 获取关联 Level |
| `SetLevel` | `void SetLevel(TSoftObjectPtr<UWorld>)` | 设置关联 Level |
| `GetNoteText` | `FString GetNoteText()` | 获取备注 |
| `SetNoteText` | `void SetNoteText(FString)` | 设置备注 |
| `AppendToNoteText` | `void AppendToNoteText(FString)` | 追加备注 |
| `GetProductionID` | `FGuid GetProductionID()` | 获取 Production ID |
| `GetProductionName` | `FString GetProductionName()` | 获取 Production 名称 |
| `GetParentAssembly` | `TSoftObjectPtr<UCineAssembly> GetParentAssembly()` | 获取父 Assembly |
| `SetParentAssembly` | `void SetParentAssembly(TSoftObjectPtr<UCineAssembly>)` | 设置父 Assembly |
| `GetFullMetadataString` | `FString GetFullMetadataString()` | 获取全部元数据的 JSON |
| `SetMetadataAsString` | `void SetMetadataAsString(FString Key, FString Value)` | 设置字符串元数据 |
| `SetMetadataAsBool` | `void SetMetadataAsBool(FString Key, bool Value)` | 设置布尔元数据 |
| `SetMetadataAsInteger` | `void SetMetadataAsInteger(FString Key, int32 Value)` | 设置整数元数据 |
| `SetMetadataAsFloat` | `void SetMetadataAsFloat(FString Key, float Value)` | 设置浮点元数据 |
| `SetMetadataAsTokenString` | `void SetMetadataAsTokenString(FString Key, FTemplateString Value)` | 设置带令牌的元数据 |
| `GetMetadataAsString` | `bool GetMetadataAsString(FString Key, FString& OutValue)` | 读取字符串元数据 |
| `GetMetadataAsBool` | `bool GetMetadataAsBool(FString Key, bool& OutValue)` | 读取布尔元数据 |
| `GetMetadataAsInteger` | `bool GetMetadataAsInteger(FString Key, int32& OutValue)` | 读取整数元数据 |
| `GetMetadataAsFloat` | `bool GetMetadataAsFloat(FString Key, float& OutValue)` | 读取浮点元数据 |

### 元数据与 Asset Registry

Assembly 的元数据通过 JSON 对象序列化。加载时，每个元数据键会自动注册为命名令牌，使得 `{cat.metadata_key}` 语法可以在名称模板中使用。

元数据还会作为 Asset Registry Tag 暴露，可以在 Content Browser 中进行搜索和过滤。

### 子序列创建流程

1. `SetSchema()` 从 Schema 读取 `SubsequencesToCreate` 和 `FoldersToCreate`
2. `CreateSubAssemblies()` 被调用时：
   - 先创建 Schema 定义的文件夹
   - 对每个子序列名称，解析令牌后创建新的 `UCineAssembly`
   - 设置子序列的 Level、Parent、Production 引用
   - 复制父序列的 Playback Range
   - 在父序列的 MovieScene 中添加 SubTrack 和 SubSection

## 核心类：UCineAssemblySchema

Schema 是 Assembly 的模板定义。它定义了：

- Assembly 的默认命名规则
- 需要创建的子序列列表
- 需要创建的文件夹列表
- 元数据字段定义（类型、键名、默认值）
- 父 Schema 约束
- 缩略图

### 关键属性

```cpp
// Schema 名称，作为 Assembly 的 "类型" 标识
FString SchemaName;

// Schema 描述
FString Description;

// Assembly 默认名称模板
FString DefaultAssemblyName;

// Assembly 默认路径
FString DefaultAssemblyPath;

// 父 Schema 约束（限制哪些 Schema 可以作为父 Assembly）
FSoftObjectPath ParentSchema;

// 缩略图
TObjectPtr<UTexture2D> ThumbnailImage;

// 元数据字段定义列表
TArray<FAssemblyMetadataDesc> AssemblyMetadata;

// 子序列名称列表
TArray<FString> SubsequencesToCreate;

// 文件夹名称列表
TArray<FString> FoldersToCreate;

// 模板 Level Sequence
FSoftObjectPath Template;

// 子序列模板映射
TMap<FString, FSoftObjectPath> SubsequenceTemplates;

// Data-Only 标记
bool bIsDataOnly = false;
```

### 元数据类型枚举

```cpp
enum class ECineAssemblyMetadataType : uint8
{
    String = 0,    // 字符串
    Bool,          // 布尔
    Integer,       // 整数
    Float,         // 浮点
    AssetPath,     // 资产路径（可限制资产类型）
    CineAssembly   // Assembly 引用（可限制 Schema 类型）
};
```

### FAssemblyMetadataDesc 结构

每个元数据字段由 `FAssemblyMetadataDesc` 描述：

| 字段 | 说明 |
|---|---|
| `Type` | 元数据类型 |
| `Key` | 元数据键名 |
| `AssetClass` | AssetPath 类型时限制的资产类 |
| `SchemaType` | CineAssembly 类型时限制的 Schema |
| `DefaultValue` | 默认值（TVariant） |
| `bEvaluateTokens` | 字符串类型是否评估令牌 |

## 核心类：UCineAssemblyNamingTokens

继承自 `UNamingTokens`，为 CAT 系统提供命名令牌功能。命名空间为 `cat`。

### 内置令牌

| 令牌 | 语法 | 说明 |
|---|---|---|
| Assembly Name | `{cat.assembly}` | Assembly 的解析后名称 |
| Base Schema | `{cat.schema}` | Schema 名称 |
| Target Level | `{cat.level}` | 关联 Level 的资产名 |
| Parent Assembly | `{cat.parent}` | 父 Assembly 的资产名 |
| Production | `{cat.production}` | Production 名称 |
| Author | `{cat.author}` | 作者（仅编辑器） |
| Created | `{cat.created}` | 创建时间（仅编辑器） |
| Date Created | `{cat.dateCreated}` | 创建日期（仅编辑器） |
| Time Created | `{cat.timeCreated}` | 创建时间戳（仅编辑器） |

此外，每个元数据键也会动态注册为令牌，语法为 `{cat.<metadata_key>}`。

### 使用方法

```cpp
// 解析包含令牌的字符串
FText Resolved = UCineAssemblyNamingTokens::GetResolvedText(
    TEXT("{cat.assembly}_{cat.production}"),
    MyAssembly
);

// 添加自定义元数据令牌
UCineAssemblyNamingTokens* Tokens = /* 获取实例 */;
Tokens->AddMetadataToken(TEXT("ShotNumber"));
// 之后就可以使用 {cat.ShotNumber} 了
```

## 模块依赖

### Public 依赖

| 模块 | 用途 |
|---|---|
| `Engine` | 核心引擎 |
| `LevelSequence` | Level Sequence 基础设施 |
| `NamingTokens` | 命名令牌系统 |

### Private 依赖

| 模块 | 用途 |
|---|---|
| `Core` | 核心模块 |
| `CoreUObject` | UObject 系统 |
| `Json` | JSON 解析 |
| `JsonUtilities` | JSON 工具 |
| `MovieScene` | Sequencer 场景图 |
| `SlateCore` | Slate UI 核心 |
| `UniversalObjectLocator` | 对象定位器 |
