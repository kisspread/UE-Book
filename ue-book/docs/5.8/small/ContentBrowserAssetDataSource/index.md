# Content Browser - Asset Data Source

> Data Source plugin providing Asset Data to the Content Browser

| 属性 | 值 |
|---|---|
| 中文名 | 内容浏览器资产数据源 |
| 分类 | Content Browser |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ContentBrowserAssetDataSource` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ContentBrowser/ContentBrowserAssetDataSource) | |

## 用途

此插件是 **UE5 内容浏览器重构后的核心组件之一**。在 UE5 中，内容浏览器被设计为可扩展架构，允许不同的数据源（如资产、关卡等）通过统一接口（`UContentBrowserDataSource`）向其提供数据。

`ContentBrowserAssetDataSource` 正是**标准资产（UAsset）的数据源实现**。它负责：
1.  **数据桥接**：将 `IAssetRegistry` 中的资产数据（`FAssetData`）转换为内容浏览器可理解的 `FContentBrowserItemData` 项。
2.  **功能实现**：实现所有对资产和文件夹的编辑器操作，包括浏览、过滤、右键菜单（重命名、删除、复制、移动等）、拖放等。
3.  **过滤系统**：编译和执行复杂的资产过滤条件（类、路径、集合等），为内容浏览器的搜索和浏览功能提供支持。

简单来说，没有这个插件，UE5 的内容浏览器将无法知道项目中存在哪些资产，也无法对这些资产进行任何操作。

## 使用场景

-   **UE5 项目开发**：此插件是默认启用的，所有使用内容浏览器（默认面板）的开发者都在隐式地使用它。你不需要直接关心它，但它的正确工作是内容浏览器功能的基础。
-   **扩展内容浏览器**：如果你需要创建自定义的资产数据源（例如，显示来自特定服务器或数据库的资产），你可以参考此插件的实现模式，继承 `UContentBrowserDataSource` 并实现类似的接口。
-   **深度集成编辑器工具**：某些高级编辑器工具或自动化流程可能需要与内容浏览器的底层数据模型交互，此时了解此插件提供的核心工具函数会很有帮助。

## 蓝图用法

此插件主要为 **C++ 编辑器扩展** 设计，**不直接暴露 `BlueprintCallable` 节点**给蓝图系统。其功能通过内容浏览器的UI和C++ API调用。

## C++ 用法

### 头文件引入

主要的工具函数位于一个独立的命名空间中：
```cpp
#include "ContentBrowserAssetDataCore.h"
```

核心数据源类：
```cpp
#include "ContentBrowserAssetDataSource.h"
```

### 基本用法 (工具函数)

插件提供了一系列静态工具函数（`ContentBrowserAssetData` 命名空间下）用于创建和操作资产项数据。这些函数通常在自定义数据源或需要处理内容浏览器项的其他编辑器模块中使用。

**示例：创建一个资产文件项的数据**（源自测试或实际数据源实现逻辑）
```cpp
// 假设我们有一个 FAssetData 和所属的数据源指针
UContentBrowserDataSource* MyDataSource = ...;
FAssetData SomeAsset = ...;
FName VirtualPath = TEXT("/Game/MyFolder/MyAsset");

// 创建用于内容浏览器显示的项数据
FContentBrowserItemData FileItem = ContentBrowserAssetData::CreateAssetFileItem(
    MyDataSource,
    VirtualPath,
    SomeAsset.PackageName, // 内部路径通常就是包名
    SomeAsset,
    false // bIsPlugin
);

// 检查创建是否成功
if (FileItem.IsValid())
{
    // 项数据创建成功，可以将其传递给内容浏览器系统
    // ...
}
```

**示例：获取项的数据负载（Payload）并执行操作**
```cpp
// 从已有的 FContentBrowserItemData 获取负载，以访问资产具体信息
TSharedPtr<const FContentBrowserAssetFileItemDataPayload> Payload = 
    ContentBrowserAssetData::GetAssetFileItemPayload(MyDataSource, FileItem);

if (Payload.IsValid())
{
    // 获取实际的资产数据
    const FAssetData& AssetData = Payload->GetAssetData();
    UE_LOG(LogTemp, Log, TEXT("操作资产: %s"), *AssetData.AssetName.ToString());

    // 尝试加载资产（如果需要）
    UObject* AssetObject = Payload->GetAsset(true);
    if (AssetObject)
    {
        // 对资产进行操作...
    }
}
```

### 进阶用法 (实现自定义数据源)

创建一个完整的资产数据源需要继承 `UContentBrowserDataSource` 并实现其虚函数。`UContentBrowserAssetDataSource` 类本身就是一个完整的范例。

**关键步骤概览：**
1.  **继承**：创建 `UMyCustomDataSource : public UContentBrowserDataSource`。
2.  **实现过滤**：重写 `CompileFilter`，使用 `PopulateAssetFilterInputParams`, `CreatePathFilter`, `CreateAssetFilter` 等静态辅助函数来构建过滤器。
3.  **实现枚举**：重写 `EnumerateItemsMatchingFilter`，使用 `EnumerateFoldersMatchingFilter` 和自定义逻辑来遍历符合过滤器的项。
4.  **实现操作**：重写 `CanRenameItem`, `RenameItem`, `CanDeleteItem`, `DeleteItem` 等函数，将内容浏览器的请求转发到你自己的资产管理系统。

## Demo 示例

以下是一个简化的自定义资产数据源骨架，演示如何利用 `ContentBrowserAssetDataSource` 模块提供的工具。

**MyDataSource.h**
```cpp
#pragma once

#include "ContentBrowserDataSource.h"
#include "MyDataSource.generated.h"

UCLASS()
class UMyDataSource : public UContentBrowserDataSource
{
    GENERATED_BODY()

public:
    virtual void Initialize(const bool bAutoRegister = true) override;
    virtual void Shutdown() override;

    // 编译过滤器
    virtual void CompileFilter(const FName InPath, const FContentBrowserDataFilter& InFilter, FContentBrowserDataCompiledFilter& OutCompiledFilter) override;

    // 枚举匹配过滤器的项
    virtual void EnumerateItemsMatchingFilter(const FContentBrowserDataCompiledFilter& InFilter, TFunctionRef<bool(FContentBrowserItemData&&)> InCallback) override;

    // 示例：实现重命名
    virtual bool CanRenameItem(const FContentBrowserItemData& InItem, const FString* InNewName, const IContentBrowserHideFolderIfEmptyFilter* HideFolderIfEmptyFilter, FText* OutErrorMsg) override;
    virtual bool RenameItem(const FContentBrowserItemData& InItem, const FString& InNewName, FContentBrowserItemData& OutNewItem) override;

private:
    // 你的数据管理成员
    TMap<FName, FMyAssetRecord> AssetRecords;
};
```

**MyDataSource.cpp**
```cpp
#include "MyDataSource.h"
#include "ContentBrowserAssetDataCore.h" // 引入工具函数

void UMyDataSource::Initialize(const bool bAutoRegister)
{
    Super::Initialize(bAutoRegister);
    // 初始化你的数据源，注册到ContentBrowserModule等
}

void UMyDataSource::Shutdown()
{
    // 清理
    Super::Shutdown();
}

void UMyDataSource::CompileFilter(const FName InPath, const FContentBrowserDataFilter& InFilter, FContentBrowserDataCompiledFilter& OutCompiledFilter)
{
    // 1. 填充过滤器输入参数
    UContentBrowserAssetDataSource::FAssetFilterInputParams Params;
    bool bSuccess = UContentBrowserAssetDataSource::PopulateAssetFilterInputParams(
        Params, this, GetAssetRegistry(), InFilter, OutCompiledFilter);

    if (!bSuccess) return;

    // 2. 创建路径过滤器（处理文件夹）
    UContentBrowserAssetDataSource::CreatePathFilter(Params, InPath, InFilter, OutCompiledFilter,
        [this](FName Path, TFunctionRef<bool(FName)> Callback, bool bRecurse) {
            // 你自己的子路径枚举逻辑
            // Callback(SubPath);
        });

    // 3. 创建资产过滤器（处理文件）
    UContentBrowserAssetDataSource::CreateAssetFilter(Params, InPath, InFilter, OutCompiledFilter);
}

void UMyDataSource::EnumerateItemsMatchingFilter(const FContentBrowserDataCompiledFilter& InFilter, TFunctionRef<bool(FContentBrowserItemData&&)> InCallback)
{
    // 获取编译好的过滤器
    const FContentBrowserCompiledAssetDataFilter* AssetFilter = InFilter.GetFilter<FContentBrowserCompiledAssetDataFilter>();

    // 1. 枚举文件夹
    UContentBrowserAssetDataSource::EnumerateFoldersMatchingFilter(this, AssetFilter, InCallback,
        [](FName Path, TFunctionRef<bool(FName)> Callback, bool bRecurse) { /* 你的逻辑 */ },
        [this](FName Path) -> FContentBrowserItemData {
            return ContentBrowserAssetData::CreateAssetFolderItem(this, Path, Path);
        });

    // 2. 枚举资产文件（需遍历你的AssetRecords并检查过滤器）
    for (const auto& Pair : AssetRecords)
    {
        if (AssetFilter && !UContentBrowserAssetDataSource::PathPassesCompiledDataFilter(*AssetFilter, Pair.Key))
            continue;

        FContentBrowserItemData Item = ContentBrowserAssetData::CreateAssetFileItem(this, Pair.Key, Pair.Value.InternalPath, Pair.Value.AssetData);
        if (!InCallback(MoveTemp(Item)))
            break; // 回调返回false，停止枚举
    }
}

bool UMyDataSource::CanRenameItem(const FContentBrowserItemData& InItem, const FString* InNewName, const IContentBrowserHideFolderIfEmptyFilter* HideFolderIfEmptyFilter, FText* OutErrorMsg)
{
    // 利用工具函数检查基本条件
    return ContentBrowserAssetData::CanRenameItem(
        GetAssetTools(), this, InItem, InNewName, OutErrorMsg);
}

bool UMyDataSource::RenameItem(const FContentBrowserItemData& InItem, const FString& InNewName, FContentBrowserItemData& OutNewItem)
{
    // 执行你自己的重命名逻辑
    // 成功后，可能需要创建一个新的FContentBrowserItemData代表重命名后的项
    // OutNewItem = ContentBrowserAssetData::CreateAssetFileItem(...);
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 获取项目中的资产元数据 (`FAssetData`) |
| `AssetTools` | 执行资产操作（复制、移动、删除、导入等） |
| `CollectionManager` | 处理资产集合（Collection）相关的过滤和操作 |
| `ContentBrowser` | 核心内容浏览器模块，提供 `UContentBrowserDataSource` 基类和数据类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏迁移到新的 `UE_LOGF`。 |
| 2026-04-07 | `4389d9d2` | When right clicking asset, show reason asset cannot be made public in tooltip if asset class does no... | 优化右键菜单，当资产无法公开时在工具提示中显示原因。 |
| 2026-04-03 | `d9cd2d24` | [ContentBrowser] Add validity check before populating sub menu array | 在填充子菜单数组前增加有效性检查，避免潜在问题。 |
| 2026-04-03 | `14713bdd` | [ContentBrowser] Logic changes for the new Add Menu | 为新的“添加”菜单调整逻辑。 |
| 2026-03-30 | `694143e8` | UE_DEPRECATED text should not be wrapped in TEXT() | 修正废弃宏的用法。 |

### 维护评价

-   **活跃维护**：从提交历史看，Epic 持续在优化和维护此插件。最近半年有多次功能性更新和错误修复，涉及UI逻辑、菜单系统、日志规范等，表明其仍在积极开发中。
-   **核心地位**：作为 UE5 内容浏览器的标准资产数据源，它是编辑器基础设施的关键部分，预计将得到长期支持。
-   **推荐使用**：对于需要与内容浏览器底层资产数据交互的编辑器扩展，此插件是官方推荐的参考和工具来源。直接使用或继承其模式是稳定可靠的选择。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ContentBrowser/ContentBrowserAssetDataSource)
-   [官方文档]() （暂无）
-   [测试用例]() （此插件的测试可能位于 `Engine/Tests/Editor/ContentBrowser/` 目录下，需进一步确认）