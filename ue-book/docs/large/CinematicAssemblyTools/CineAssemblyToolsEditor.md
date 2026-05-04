# CineAssemblyToolsEditor（Editor 模块）

> Editor 模块，提供 Production 设置管理、编辑器 UI、Take Recorder 集成、资产定义和属性自定义。

## 模块概览

| 属性 | 值 |
|---|---|
| 模块名 | `CineAssemblyToolsEditor` |
| 类型 | Editor |
| 加载阶段 | Default |
| 源文件数 | 约 47 个（.h + .cpp） |

### 源文件组织

```
CineAssemblyToolsEditor/
├── Public/
│   ├── ICineAssemblyToolsEditorModule.h    # 模块公开接口
│   ├── ProductionSettings.h                # Production 设置（核心配置类）
│   └── ScopedModifyProductionExtendedData.h # 扩展数据修改守卫
├── Private/
│   ├── CineAssemblyToolsEditorModule.*     # 模块实现
│   ├── ProductionFunctionLibrary.*         # 蓝图函数库
│   ├── ProductionExtensions.*              # Production 扩展数据系统
│   ├── ProductionSettings.*                # Production 设置实现
│   ├── ProductionSettingsCustomization.*   # Production 设置属性自定义
│   ├── CinematicProductionCustomization.*  # Production 结构体属性自定义
│   ├── CineAssemblyCustomization.*         # Assembly 属性自定义
│   ├── CineAssemblySchemaCustomization.*   # Schema 属性自定义
│   ├── CineAssemblyMetadataCustomization.* # 元数据属性自定义
│   ├── CineAssemblyFactory.*               # Assembly 资产工厂
│   ├── CineAssemblySchemaFactory.*         # Schema 资产工厂
│   ├── AssetDefinition_CineAssembly.*      # Assembly 资产类型定义
│   ├── AssetDefinition_CineAssemblySchema.*# Schema 资产类型定义
│   ├── CineAssemblyToolsAnalytics.*        # 分析事件
│   ├── CineAssemblyToolsStyle.*            # Slate 样式
│   ├── LeadingZeroNumericTypeInterface.*   # 前导零数字输入
│   ├── TakeRecorder/
│   │   ├── CineAssemblyTakeRecorderIntegration.* # Take Recorder 集成
│   │   └── CineAssemblyTakeRecorderSettings.*    # Take Recorder 设置
│   └── UI/
│       ├── SProductionWizard.*             # Production Wizard 主窗口
│       ├── SProductionListPanel.*          # Production 列表面板
│       ├── SActiveProductionCombo.*        # 活跃 Production 下拉框
│       ├── SActiveProductionExtendedDataDetailsView.* # 扩展数据详情
│       ├── SFolderHierarchyPanel.*         # 文件夹层级面板
│       ├── SAssetNamingPanel.*             # 资产命名面板
│       ├── SNamingTokensPanel.*            # 命名令牌面板
│       ├── SSequencerSettingsPanel.*       # Sequencer 设置面板
│       ├── SRevisionControlPanel.*         # 版本控制面板
│       └── CineAssembly/
│           ├── SCineAssemblyPropertyEditor.*   # Assembly 属性编辑器
│           ├── SCineAssemblyConfigWindow.*     # Assembly 配置窗口
│           ├── SCineAssemblyConfigPanel.*      # Assembly 配置面板
│           ├── SCineAssemblySchemaWindow.*     # Schema 编辑窗口
│           └── SDuplicateAssemblyWindow.*      # Assembly 复制窗口
```

## 核心类：UProductionSettings

`UProductionSettings` 继承自 `UDeveloperSettings`，是 CAT 的配置中心。它管理一组 `FCinematicProduction` 对象，每个 Production 定义了一组项目级设置。

### FCinematicProduction 结构

```cpp
struct FCinematicProduction
{
    FGuid ProductionID;                          // 唯一 ID
    FString ProductionName;                      // 制作项目名称
    FFrameRate DefaultDisplayRate;               // 默认帧率
    int32 DefaultStartFrame;                     // 默认起始帧
    ESubsequencePriority SubsequencePriority;    // 子序列优先级
    TSet<FString> NamingTokenNamespaceDenyList;  // 命名令牌命名空间黑名单
    TMap<const UClass*, FString> DefaultAssetNames; // 默认资产名称
    TArray<FFolderTemplate> TemplateFolders;     // 模板文件夹层级
    // ExtendedData: 可扩展的自定义数据
};
```

### 子序列优先级

```cpp
enum class ESubsequencePriority : uint8
{
    TopDown,    // 父序列优先级高于子序列
    BottomUp    // 子序列优先级高于父序列（默认）
};
```

### Production 管理 API

| 方法 | 说明 |
|---|---|
| `GetProductions()` | 获取所有 Production 列表 |
| `GetProduction(FGuid)` | 按 ID 获取 Production |
| `AddProduction()` | 添加新 Production |
| `DuplicateProduction(FGuid)` | 复制 Production |
| `DeleteProduction(FGuid)` | 删除 Production |
| `RenameProduction(FGuid, FString)` | 重命名 Production |
| `GetActiveProduction()` | 获取活跃 Production |
| `SetActiveProduction(FGuid)` | 设置活跃 Production |
| `IsActiveProduction(FGuid)` | 检查是否为活跃 Production |

### 项目覆盖

当设置活跃 Production 时，CAT 会自动覆盖以下项目设置：

| 设置 | 来源 |
|---|---|
| `DefaultDisplayRate` | Sequencer 默认帧率 |
| `DefaultStartFrame` | Sequencer 默认起始帧 |
| `Subsequence Hierarchical Bias` | 子序列层级偏移 |
| `DefaultAssetNames` | 资产工具默认名称 |

### 扩展数据系统

Production 支持通过 `ExtendedData` 机制扩展自定义数据：

```cpp
// 注册扩展类型
ICineAssemblyToolsEditorModule& Module = ICineAssemblyToolsEditorModule::Get();
Module.RegisterProductionExtension(*FMyStruct::StaticStruct());

// 访问扩展数据
UProductionSettings* Settings = GetMutableDefault<UProductionSettings>();
TConstStructView<FMyStruct> Data = Settings->GetProductionExtendedData<FMyStruct>(ProductionID);

// 修改扩展数据（使用 RAII 守卫）
FScopedModifyProductionExtendedData Guard = Settings->ModifyProductionExtendedData(ProductionID);
TStructView<FMyStruct> MutableData = Settings->GetMutableProductionExtendedData<FMyStruct>(ProductionID);
MutableData.Get().MyField = NewValue;
// Guard 销毁时自动导出回配置
```

## 核心类：UProductionFunctionLibrary

蓝图函数库，提供所有 CAT 的蓝图可调用接口。

### Production 管理

| 节点 | 签名 | 说明 |
|---|---|---|
| `GetAllProductions` | `TArray<FCinematicProduction>` | 获取所有 Production |
| `GetProduction` | `bool (FGuid, FCinematicProduction&)` | 按 ID 获取 |
| `GetActiveProduction` | `bool (FCinematicProduction&)` | 获取活跃 Production |
| `SetActiveProduction` | `void (FCinematicProduction)` | 设置活跃 Production |
| `SetActiveProductionByID` | `void (FGuid)` | 按 ID 设置活跃 Production |
| `ClearActiveProduction` | `void()` | 清除活跃 Production |
| `IsActiveProduction` | `bool (FGuid)` | 检查是否活跃 |
| `AddProduction` | `void (FCinematicProduction)` | 添加 Production |
| `DeleteProduction` | `void (FGuid)` | 删除 Production |
| `RenameProduction` | `void (FGuid, FString)` | 重命名 Production |

### Assembly 操作

| 节点 | 签名 | 说明 |
|---|---|---|
| `CreateAssembly` | `UCineAssembly* (Schema, Level, Parent, Metadata, Path, Name, bUseDefaultName)` | 创建 Assembly |

### 扩展数据操作

| 节点 | 签名 | 说明 |
|---|---|---|
| `GetProductionExtendedData` | `bool (FGuid, UScriptStruct*, FInstancedStruct&)` | 获取扩展数据 |
| `SetProductionExtendedData` | `bool (FGuid, FInstancedStruct)` | 设置扩展数据 |

## 核心接口：ICineAssemblyToolsEditorModule

Editor 模块的公开接口，允许其他插件扩展 CAT 的功能。

### Production 扩展注册

```cpp
// 注册自定义 Production 扩展数据类型
virtual void RegisterProductionExtension(const UScriptStruct& DataScriptStruct) = 0;
virtual void UnregisterProductionExtension(const UScriptStruct& DataScriptStruct) = 0;
```

### Production Wizard 自定义

```cpp
// 为扩展数据注册 Wizard 自定义
virtual void RegisterProductionWizardCustomization(
    const UScriptStruct& ForDataScriptStruct,
    FGetWidget MakeCustomWidget,        // 自定义 Widget 构造回调
    TAttribute<FText> Label,            // 标签
    TAttribute<FSlateIcon> Icon,        // 图标
    bool bShowProductionSelection,      // 是否显示 Production 选择器
    bool bHideInWizard                  // 是否在 Wizard 中隐藏
) = 0;

// 注册自定义 User Settings 标签页
virtual void RegisterProductionWizardUserSettings(
    FName Name,
    FGetWidget MakeCustomWidget,
    TAttribute<FText> Label,
    TAttribute<FSlateIcon> Icon
) = 0;
```

## 编辑器 UI

### Production Wizard

通过 `Tools > Cinematics > Production Wizard` 菜单访问。Production Wizard 是一个可停靠的 Nomad 标签页，提供以下面板：

| 面板 | 说明 |
|---|---|
| Production List | 管理所有 Production（添加、删除、重命名、复制） |
| Active Production Combo | 快速切换活跃 Production |
| Sequencer Settings | 帧率、起始帧、子序列优先级 |
| Folder Hierarchy | 模板文件夹层级管理 |
| Asset Naming | 默认资产名称配置 |
| Naming Tokens | 命名令牌命名空间黑名单 |
| Revision Control | 版本控制相关设置 |

### Assembly 属性编辑器

双击 Assembly 资产时打开的自定义编辑窗口，替代默认的 Sequencer 编辑器：

- 显示 Assembly 的所有属性和元数据
- 支持编辑关联 Level、父 Assembly、Production
- 元数据编辑支持各种类型（String、Bool、Int、Float、AssetPath、CineAssembly）
- Data-Only 模式下只显示详情面板

### Schema 编辑窗口

双击 Schema 资产时打开的编辑窗口：

- 编辑 Schema 名称、描述、默认 Assembly 名称
- 管理元数据字段定义
- 管理子序列和文件夹模板
- 设置父 Schema 约束

## Take Recorder 集成

`FCineAssemblyTakeRecorderIntegration` 管理 CAT 与 Take Recorder 的交互：

| 回调 | 说明 |
|---|---|
| `OnRecordingInitialized` | 录制初始化时 |
| `OnRecordingStarted` | 录制开始时 |
| `OnTickRecording` | 录制每帧更新 |
| `OnRecordingStopped` | 录制停止时 |

通过 `CineAssemblyTakeRecorderSettings` 可以配置 Take Recorder 与 Assembly 的关联行为。

## 资产工厂

### CineAssemblyFactory

创建新的 CineAssembly 资产时使用的工厂类。处理：

- 从 Content Browser 右键菜单创建
- 使用 Schema 模板初始化
- 设置默认名称和路径

### CineAssemblySchemaFactory

创建新的 CineAssemblySchema 资产时使用的工厂类。

## 属性自定义

Editor 模块注册了多个属性自定义，改善编辑体验：

| 自定义类 | 目标 | 说明 |
|---|---|---|
| `FProductionSettingsCustomization` | `UProductionSettings` | Production 设置的详情面板自定义 |
| `FCinematicProductionCustomization` | `FCinematicProduction` | Production 结构体的属性自定义 |
| `FCineAssemblyCustomization` | `UCineAssembly` | Assembly 资产的属性自定义 |
| `FCineAssemblySchemaCustomization` | `UCineAssemblySchema` | Schema 资产的属性自定义 |
| `FCineAssemblyMetadataCustomization` | `FAssemblyMetadataDesc` | 元数据描述的属性自定义 |

## 其他组件

### FProductionExtensions

管理 Production 扩展数据的注册和生命周期。跟踪所有注册的 `UScriptStruct` 类型。

### FLeadingZeroNumericTypeInterface

为数字输入框提供前导零支持，用于镜头号等需要固定位数的场景。

### FCineAssemblyToolsAnalytics

分析事件跟踪，记录 CAT 的使用情况。

### FCineAssemblyToolsStyle

Slate 样式定义，提供 CAT 专用的 UI 图标和样式。

## 模块依赖

### Private 依赖（主要）

| 模块 | 用途 |
|---|---|
| `CineAssemblyTools` | Runtime 模块（Assembly、Schema） |
| `LevelSequenceEditor` | Sequencer 编辑器集成 |
| `TakeRecorder` | Take Recorder 集成 |
| `TakesCore` | Takes 核心功能 |
| `MovieRenderPipelineCore` | 渲染管线集成 |
| `NamingTokens` | 命名令牌系统 |
| `PropertyEditor` | 属性编辑器自定义框架 |
| `AssetDefinition` | 资产类型定义框架 |
| `AssetTools` | 资产工具 |
| `ContentBrowser` | Content Browser 集成 |
| `SourceControl` | 版本控制集成 |
| `ToolMenus` | 菜单扩展框架 |
| `UnrealEd` | 编辑器核心 |
| `DirectoryPlaceholder` | 目录占位符 |
| `SharedSettingsWidgets` | 共享设置 Widget |
| `EditorWidgets` | 编辑器 Widget |
| `StructUtilsEditor` | 结构体工具（编辑器） |
