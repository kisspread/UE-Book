# Content Browser - Class Data Source

> Data Source plugin providing Class Data to the Content Browser

| 属性 | 值 |
|---|---|
| 分类 | Content Browser |
| 默认启用 | ✅ true |
| 包含内容 | ❌ false |
| 模块 | ContentBrowserClassDataSource (Editor) |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董 (>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/ContentBrowser/ContentBrowserClassDataSource) | |

## 用途

ContentBrowserClassDataSource 是 UE5 Content Browser 数据源架构的一个实现，负责将 **原生 C++ 类层级**（Native Class Hierarchy）以虚拟文件夹的形式暴露给 Content Browser。

在 UE5 的 Content Browser 重构中，资产浏览不再局限于磁盘上的 `.uasset` 文件，而是通过 `UContentBrowserDataSource` 的插件化机制支持多种数据源。本 plugin 就是其中专用于"类"的数据源——它让 Content Browser 能够像浏览资产一样浏览项目中的 C++ 类和蓝图类的继承树。

核心工作原理：

1. **模块启动时**自动创建 `UContentBrowserClassDataSource` 实例并注册到 Content Browser 数据子系统
2. 构建一个 `FNativeClassHierarchy`，扫描引擎和项目中的所有原生类
3. 将类的继承关系映射为虚拟路径树（路径前缀为 `/Classes_`）
4. 响应 Content Browser 的过滤、枚举、属性查询等请求

## 使用场景

- **浏览类继承树**：在 Content Browser 的 Classes 视图中，按文件夹结构浏览所有 C++ 类和蓝图类
- **创建新类**：在 Content Browser 右键菜单中选择"新建 C++ 类"，自动定位到选中的类路径下
- **按 Collection 过滤类**：通过 UE 的 Collection 系统对类进行分组和筛选
- **编辑器扩展开发**：作为 `UContentBrowserDataSource` 的参考实现，用于开发自定义数据源

## 蓝图用法

本 plugin **没有暴露任何蓝图接口**。它是纯编辑器内部基础设施，所有功能通过 Content Browser UI 或 C++ API 间接使用。

## C++ 用法

本 plugin 的主要价值在于作为 Content Browser 数据源架构的参考实现。普通项目一般不需要直接与之交互。

### 作为参考实现：自定义数据源

如果你需要为 Content Browser 添加自定义数据源（例如浏览数据库记录、远程资源等），可以参考本 plugin 的模式：

```cpp
// 继承 UContentBrowserDataSource
UCLASS()
class UMyCustomDataSource : public UContentBrowserDataSource
{
    GENERATED_BODY()

public:
    // 初始化时注册到 Content Browser
    void Initialize(bool bInAutoRegister = true);

    // 编译过滤器——将通用过滤器转换为本数据源的特定过滤器
    virtual void CompileFilter(
        const FName InPath,
        const FContentBrowserDataFilter& InFilter,
        FContentBrowserDataCompiledFilter& OutCompiledFilter) override;

    // 枚举匹配过滤器的项目
    virtual void EnumerateItemsMatchingFilter(
        const FContentBrowserDataCompiledFilter& InFilter,
        TFunctionRef<bool(FContentBrowserItemData&&)> InCallback) override;

    // ... 其他虚函数重写
};
```

### 关键虚函数说明

| 函数 | 说明 |
|---|---|
| `Initialize` | 注册数据源，构建虚拟路径树，绑定菜单扩展 |
| `Shutdown` | 清理资源，取消注册 |
| `CompileFilter` | 将 Content Browser 的通用过滤器编译为数据源特定的过滤条件 |
| `EnumerateItemsMatchingFilter` | 根据编译后的过滤器枚举匹配的文件和文件夹项 |
| `EnumerateItemsAtPath` | 枚举指定路径下的子项 |
| `EnumerateItemsAtUserProvidedPath` | 处理用户在地址栏输入的路径（如 `/Script/Engine.Actor`） |
| `EnumerateItemsForObjects` | 从 UObject 数组反查对应的 Content Browser 项 |
| `IsFolderVisible` | 判断文件夹是否应该显示 |
| `DoesItemPassFilter` | 判断单个项是否通过过滤器 |
| `GetItemAttribute(s)` | 获取项的属性（名称、类型、大小等） |
| `GetItemPhysicalPath` | 获取项的磁盘路径（类数据源中类没有物理路径） |
| `CanEditItem` / `EditItem` | 判断/执行编辑操作 |
| `BuildRootPathVirtualTree` | 构建虚拟路径树的根节点 |

### 模块启动流程

来源：`ContentBrowserClassDataSourceModule.cpp`

```cpp
// 模块在 StartupModule 中创建数据源实例
class FContentBrowserClassDataSourceModule : public FDefaultModuleImpl
{
    virtual void StartupModule() override
    {
        ClassDataSource.Reset(NewObject<UContentBrowserClassDataSource>(
            GetTransientPackage(), "ClassData"));
        ClassDataSource->Initialize();  // 自动注册到 ContentBrowserDataSubsystem
    }

    virtual void ShutdownModule() override
    {
        ClassDataSource.Reset();
    }

private:
    TStrongObjectPtr<UContentBrowserClassDataSource> ClassDataSource;
};
```

## Demo 示例

本 plugin 不适合作为独立 Demo 使用。以下是一个最小的自定义数据源模块的 Build.cs 示例：

```csharp
// MyCustomDataSource.Build.cs
using UnrealBuildTool;

public class MyCustomDataSource : ModuleRules
{
    public MyCustomDataSource(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "ContentBrowserData",  // 数据源基类所在模块
        });

        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "AssetTools",
            "UnrealEd",
        });
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `ContentBrowserData` | Content Browser 数据源基类 `UContentBrowserDataSource` |
| `AssetTools` | 资产类型操作接口（`IAssetTypeActions`） |
| `CollectionManager` | Collection 系统支持，用于按集合过滤类 |
| `UnrealEd` | 编辑器核心，菜单扩展、新类创建对话框 |
| `GameProjectGeneration` | "新建 C++ 类"对话框（`OpenAddCodeToProjectDialog`） |
| `ToolMenus` | UE 工具菜单系统 |
| `Slate` / `SlateCore` | UI 框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-02 | `f28b34d` | 资产视图现在可以显示 Verse 路径、对象路径或包路径 | 配合 Verse 语言集成，优化路径列显示 |
| 2025-08-19 | `916ed52` | 更新导航栏行为，点击空白区域编辑友好路径而非虚拟路径；类数据源不再通过 `Legacy_TryGetPackagePath` 返回内部路径 | 改进用户体验，避免暴露内部 `/Classes_` 路径 |
| 2025-08-18 | `2380e89` | 支持在导航栏中输入脚本包名进行跳转 | 新增对 `/Script/` 路径导航的支持 |

### 维护评价

- **年龄**：创建于 2020 年 6 月，已超过 5 年
- **活跃度**：近期（2025 年 8-9 月）仍有功能性更新，属于**活跃维护**
- **定位**：UE5 Content Browser 架构的核心组件，默认启用，不太可能被废弃
- **风险**：作为 Epic 内部基础设施，API 可能随版本变化，不建议直接依赖其内部实现
- **推荐**：✅ 适合作为学习 Content Browser 数据源架构的参考；不建议直接耦合使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/ContentBrowser/ContentBrowserClassDataSource)
- [ContentBrowserData 模块（基类所在）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/ContentBrowser)
- 测试用例：本 plugin 无独立测试文件
