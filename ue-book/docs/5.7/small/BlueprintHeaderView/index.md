# Blueprint C++ Header Preview

> A tool to help convert Blueprint Classes to Native C++.

| 属性 | 值 |
|---|---|
| 分类 | Blueprints |
| 默认启用 | ✅ 是 |
| 包含内容 | 是 |
| 模块 | BlueprintHeaderView (Editor) |
| 创建时间 | 2022-02-16 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/BlueprintHeaderView) | |

## 用途

BlueprintHeaderView 是一个编辑器工具，为 Blueprint Class 和 UserDefinedStruct 生成类似 C++ 头文件的预览视图。它的核心用途是**辅助 Blueprint 到原生 C++ 的转换**——在编辑器中直接查看某个蓝图资产"如果写成 C++ 头文件会是什么样"，包括 UCLASS/UPROPERTY/UFUNCTION 宏声明、类型名、访问修饰符等。

这个 plugin 解决的问题是：当你需要把蓝图逻辑迁移到 C++ 时，手动翻译变量类型、函数签名、宏 specifier 很容易出错。Header View 自动完成这些翻译，并高亮语法、校验命名合法性，让你可以直接复制粘贴到 C++ 头文件中。

## 使用场景

- 你有一个复杂的蓝图类，想把它迁移到 C++ 实现 → 用 Header View 查看对应的头文件声明
- 你想确认蓝图变量/函数在 C++ 层面的正确类型和签名 → 用 Header View 一目了然
- 你需要批量整理蓝图中的变量/函数，想按访问权限或内存布局排序 → 用 Header View 的排序功能

## 蓝图用法

这是一个纯编辑器 UI 插件，不提供蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "BlueprintHeaderView.h"
```

### 基本用法

BlueprintHeaderView 主要通过编辑器 UI 操作，不直接对外暴露 C++ API。但你可以在 C++ 中以编程方式打开 Header View：

```cpp
#include "BlueprintHeaderView.h"

// 为指定的 Blueprint 资产打开 Header View
FAssetData AssetData(YourBlueprintObject);
FBlueprintHeaderViewModule::OpenHeaderViewForAsset(AssetData);

// 检查某个类是否支持 Header View
bool bSupported = FBlueprintHeaderViewModule::IsClassHeaderViewSupported(YourUClass);
```

*来源：`Source/BlueprintHeaderView/Public/BlueprintHeaderView.h`*

### 编辑器操作

1. **从 Content Browser 打开**：右键点击 Blueprint 资产 → 选择 **"Open Header View"**
2. **从 Blueprint Editor 打开**：在蓝图编辑器的菜单栏中找到 Header View 入口
3. **Class Picker**：在 Header View 面板顶部的下拉菜单中可以选择/切换要查看的 Blueprint 资产
4. **右键菜单**：
   - 右键点击类名行 → 可以重命名类名（会校验 C++ 命名合法性）
   - 右键点击函数行 → 可以重命名函数或参数
   - 右键点击变量行 → 可以重命名变量
5. **双击函数行** → 跳转到蓝图中的函数图
6. **快捷键**：`Ctrl+C` 复制选中行，`Ctrl+A` 全选

### 设置

在 **编辑器偏好设置 → Plugins → Blueprint Header View** 中可以配置：

| 设置项 | 说明 | 默认值 |
|---|---|---|
| **Sort Method** | 排序方式 | None |
| **Font Size** | 字体大小 (6-72) | 9 |
| **Selection Color** | 选中行高亮颜色 | 蓝色 (0.3, 0.3, 1.0) |
| **Syntax Colors** | 语法高亮颜色 | — |

排序方式选项：

| 排序方式 | 说明 |
|---|---|
| `None` | 保持蓝图中的原始顺序 |
| `SortByAccessSpecifier` | 按访问权限分组：public → protected → private |
| `SortForOptimalPadding` | 按内存对齐优化排序，减少 C++ 结构体 padding |

语法高亮颜色可分别配置：Comment（注释）、Error（错误）、Macro（宏）、Typename（类型名）、Identifier（标识符）、Keyword（关键字）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | (公开依赖) 基础核心库 |
| `CoreUObject` | UObject 系统，蓝图资产反射 |
| `Engine` | 引擎核心，蓝图/函数/属性系统 |
| `UnrealEd` | 编辑器框架，资产编辑器集成 |
| `BlueprintGraph` | 蓝图图表节点（UK2Node_FunctionEntry 等） |
| `Slate` / `SlateCore` | UI 框架，Header View 面板渲染 |
| `EditorStyle` | 编辑器样式 |
| `InputCore` | 输入处理 |
| `ToolMenus` | 菜单扩展（Content Browser 右键菜单） |
| `AssetTools` | 资产工具集成 |
| `DeveloperSettings` | 设置面板基类 (UDeveloperSettings) |
| `WorkspaceMenuStructure` | 工作区菜单结构 |
| `ApplicationCore` | 应用核心功能 |

> 以上均为 `PrivateDependencyModuleNames`，你的项目不需要显式依赖这些模块——它们仅被 plugin 内部使用。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-05-30 | `8396b185774c` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 2/n | 编译兼容性修复：调整 DLL 导出标记位置 |
| 2024-10-22 | `98a8e0e0df23` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 清理 UE 5.2 废弃的 include order 宏 |
| 2024-06-19 | `938f456b050b` | Moved UserDefinedStruct to CoreUObject #jira UE-216472 | 功能更新：UserDefinedStruct 支持迁移到 CoreUObject 模块 |

### 维护评价

- **创建时间**: 2022-02-16，约 4 年历史，属于 🆕 较新插件
- **维护状态**: **维护中** — 最近一次更新在 2025 年 5 月，有实质性代码改动
- **更新特点**: 近期更新以编译兼容性和代码清理为主，无新功能添加
- **已知限制**: 仅支持 Blueprint Class 和 UserDefinedStruct，不支持其他蓝图资产类型
- **推荐程度**: ✅ 推荐使用。作为 Epic 官方维护的编辑器工具，稳定可靠。如果你有 Blueprint 转 C++ 的需求，这是必备工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/BlueprintHeaderView)
