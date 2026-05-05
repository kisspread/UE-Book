# Portable Object File Data Source

> Data Source plugin providing portable object (PO) file support for the Content Browser

| 属性 | 值 |
|---|---|
| 分类 | Localization |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | PortableObjectFileDataSource (Editor) |
| 创建时间 | 2023-06-21 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/Localization/PortableObjectFileDataSource) | |

## 用途

此插件为 UE5 的 Content Browser 添加了对 `.po`（Portable Object）文件的可视化支持。PO 文件是 GNU gettext 国际化标准格式，被 UE5 的本地化管线用于存储翻译文本数据。

插件的核心功能是将项目中 `Content/Localization/` 目录下的 `.po` 文件注册到 Content Browser 的文件数据源系统，使开发者可以在编辑器中直接浏览这些本地化文件，同时将它们标记为**只读**——因为 PO 文件由本地化管线管理，不应在 Content Browser 中手动创建、删除或重命名。

## 使用场景

- 你在项目中使用 UE5 本地化管线管理多语言翻译 → 安装此插件后，Content Browser 会自动显示 `Content/Localization/` 下的 `.po` 文件
- 你需要在编辑器中快速查看哪些本地化目标有翻译数据 → 此插件让 `.po` 文件以紫色图标出现在 Content Browser 中
- 你需要通过编程方式控制 `.po` 文件是否可编辑 → 使用 `RegisterCanEditFileOverride` API 注册自定义编辑权限逻辑

## 蓝图用法

此插件不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。它是一个纯编辑器数据源插件，功能完全通过 Content Browser UI 和 C++ API 提供。

## C++ 用法

### 头文件引入

```cpp
#include "IPortableObjectFileDataSourceModule.h"
```

### 基本用法：获取模块实例

```cpp
// 获取模块引用（模块必须已加载，否则断言失败）
IPortableObjectFileDataSourceModule& PODataSource = IPortableObjectFileDataSourceModule::Get();

// 安全获取模块指针（模块未加载时返回 nullptr）
IPortableObjectFileDataSourceModule* PODataSourcePtr = IPortableObjectFileDataSourceModule::GetPtr();
if (PODataSourcePtr)
{
    // 模块已加载，可以安全使用
}
```

### 进阶用法：注册 CanEdit 覆盖

插件默认将所有 `.po` 文件设为不可编辑。如果你需要基于特定条件允许编辑某些 `.po` 文件，可以注册 `CanEditFile` 覆盖处理器：

```cpp
#include "IPortableObjectFileDataSourceModule.h"

// 注册自定义编辑权限逻辑
IPortableObjectFileDataSourceModule& PODataSource = IPortableObjectFileDataSourceModule::Get();

IPortableObjectFileDataSourceModule::FCanEditFileDelegate EditDelegate;
EditDelegate.BindLambda([](const FName InFilePath, const FString& InFilename, FText* OutErrorMsg) -> bool
{
    // 示例：只允许编辑特定本地化目标的 .po 文件
    if (InFilePath.ToString().Contains(TEXT("MyGame/Localization/MyTarget")))
    {
        return true; // 允许编辑
    }

    // 其他文件保持默认的不可编辑行为
    if (OutErrorMsg)
    {
        *OutErrorMsg = FText::FromString(TEXT("Only MyTarget PO files can be edited"));
    }
    return false;
});

FDelegateHandle Handle = PODataSource.RegisterCanEditFileOverride(MoveTemp(EditDelegate));

// ... 在不再需要时取消注册
PODataSource.UnregisterCanEditFileOverride(Handle);
```

**注意**：多个 Override 会依次查询，任何一个返回 `false` 都会拒绝编辑。

## Demo 示例

此插件是一个被动的编辑器数据源，无需手动集成代码。使用方式：

1. 确保插件已启用（默认已启用）
2. 在项目中配置本地化目标（Project Settings → Localization）
3. 使用本地化仪表板（Localization Dashboard）生成翻译文件
4. 在 Content Browser 中导航到 `Content/Localization/<TargetName>/` 目录
5. `.po` 文件将以紫色（RGB: 200, 191, 231）图标显示

### Build.cs 依赖

如果你想在自己的模块中通过 C++ API 与此插件交互：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE5 核心库 |
| `CoreUObject` | UObject 系统 |
| `ContentBrowserFileDataSource` | Content Browser 文件数据源基础框架（私有依赖） |
| `Localization` | 本地化系统，用于监听本地化目标数据更新（私有依赖） |

**插件依赖**：此插件依赖 `ContentBrowserFileDataSource` 插件（已在 `.uplugin` 中声明），该插件提供了文件数据源的基础架构。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-02-18 | `96d71ab4` | 修复 `OnContentPathMounted` 中的重复挂载问题，添加 `HasFileMount` 检查防止 "File mount already registered" 错误 |
| 2025-02-17 | `6a987b5c` | 回退后重新提交：修复插件发现刷新期间的问题，用 TSet 替代 `bEnabled` 检查以正确处理已禁用插件 |
| 2025-02-07 | `32a9ddcf` | 回退版本：修复挂载重复和插件发现逻辑 |

### 维护评价

- **创建时间**：2023-06-21（约 2.8 年前）
- **维护状态**：🟢 活跃维护 — 2025 年 2 月有多次实质性 bug 修复
- **代码规模**：非常小（1 个 .h + 1 个 .cpp + 1 个 .Build.cs），功能单一明确
- **稳定性**：近期更新集中在修复挂载重复等边界条件，说明基础功能已稳定
- **推荐使用**：✅ 推荐。作为 UE5 本地化管线的配套插件，默认启用且无需额外配置

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/Localization/PortableObjectFileDataSource)
- [ContentBrowserFileDataSource 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ContentBrowser/ContentBrowserFileDataSource) — 基础框架插件
