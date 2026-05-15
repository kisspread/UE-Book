# PluginToolset

> Toolset for listing, inspecting, and creating Plugins via the AI Toolset Registry.

| 属性 | 值 |
|---|---|
| 中文名 | 插件工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PluginToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/PluginToolset) | |

## 用途

PluginToolset 是一个面向 AI 工具集注册表（Toolset Registry）的插件管理工具集。它将 UE5 的插件系统操作封装为 AI 可调用的工具，使得 AI 代理（Agent）或自动化工作流能够以编程方式完成以下任务：

- **列出**当前项目中所有已安装的插件
- **检查**任意插件的描述符元数据（名称、描述、版本、作者等）
- **创建**新插件（基于模板生成插件骨架）
- **启用/禁用**指定插件

该插件的存在意义是为 AI 辅助开发提供插件生命周期管理能力，让 AI 能够自主地发现、创建和配置插件。

## 使用场景

- 你正在构建 AI 驱动的自动开发管线，需要 AI 自动管理项目插件 → 用 PluginToolset
- 你需要通过 AI 工具集注册表批量创建插件模板 → 用 PluginToolset
- 你想让 AI 代理检查项目中哪些插件已启用、修改插件描述符元数据 → 用 PluginToolset
- 你需要通过代码/蓝图动态启用或禁用插件 → 用 PluginToolset

## 蓝图用法

PluginToolset 提供了蓝图可用的结构体和函数，核心围绕 `FPluginDescriptorToolsetInfo` 展开。

### 核心结构体

#### FPluginDescriptorToolsetInfo

插件描述符的可编辑元数据，所有字段均可蓝图读写：

| 字段 | 类型 | 说明 |
|---|---|---|
| `FriendlyName` | `FString` | 插件友好显示名称 |
| `Description` | `FString` | 插件描述文本 |
| `Category` | `FString` | 插件所属分类 |
| `VersionName` | `FString` | 面向用户的版本名称 |
| `Version` | `int32` | 数字版本号（用于比较新旧） |
| `CreatedBy` | `FString` | 创建者名称 |
| `CreatedByURL` | `FString` | 创建者链接 |
| `DocsURL` | `FString` | 文档链接 |
| `MarketplaceURL` | `FString` | 商城链接 |
| `SupportURL` | `FString` | 支持链接/邮箱 |
| `bCanContainContent` | `bool` | 是否可包含内容资产 |
| `bIsBetaVersion` | `bool` | 是否标记为 Beta |
| `bIsExperimentalVersion` | `bool` | 是否标记为实验性 |
| `bIsSealed` | `bool` | 是否密封（禁止其他插件依赖） |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetPluginEnabled` | 启用/禁用指定插件（插件不存在时抛出错误） | `UPluginToolset` |
| `CreatePlugin` | 从模板创建新插件（使用相对路径定位插件位置） | `UPluginToolset` |
| `编辑插件描述符` | 读取/修改插件的元数据字段 | `UPluginToolset` |

### 使用示例（蓝图描述）

**创建新插件：**
1. 构造一个 `FPluginDescriptorToolsetInfo` 结构体，填写 `FriendlyName`、`Description`、`Category` 等字段
2. 调用 `CreatePlugin` 节点，传入描述符信息
3. 插件将在相对路径下生成，包含 .uplugin 文件和基础目录结构

**启用/禁用插件：**
1. 调用 `SetPluginEnabled` 节点，传入插件名称和目标启用状态
2. 若插件不存在，节点将抛出错误——建议先用列表功能确认插件存在

## C++ 用法

### 头文件引入

```cpp
#include "PluginToolset.h"
```

### 基本用法

使用 `FPluginDescriptorToolsetInfo` 结构体描述插件元数据：

```cpp
// 构造插件描述符信息
FPluginDescriptorToolsetInfo DescriptorInfo;
DescriptorInfo.FriendlyName = TEXT("MyAwesomePlugin");
DescriptorInfo.Description = TEXT("A plugin that does awesome things.");
DescriptorInfo.Category = TEXT("Gameplay");
DescriptorInfo.VersionName = TEXT("1.0");
DescriptorInfo.Version = 1;
DescriptorInfo.CreatedBy = TEXT("Your Studio");
DescriptorInfo.bCanContainContent = false;
DescriptorInfo.bIsExperimentalVersion = true;
```

### 进阶用法

结合 ToolsetRegistry 注册表，将 PluginToolset 的操作暴露为 AI 可调用的工具。典型工作流：

```cpp
// 1. 注册工具到 AI 工具集注册表（由 ToolsetRegistry 模块处理）
// 2. AI 代理发现并调用 PluginToolset 提供的工具
// 3. 工具执行插件创建/查询/启禁用操作
// 4. 返回结果给 AI 代理
```

## Demo 示例

```cpp
// MyPluginManager.h
#pragma once

#include "CoreMinimal.h"
#include "PluginToolset.h"

class FMyPluginManager
{
public:
    /** 创建一个新插件 */
    static void CreateGameplayPlugin(const FString& InPluginName)
    {
        FPluginDescriptorToolsetInfo Info;
        Info.FriendlyName = InPluginName;
        Info.Description = TEXT("自动生成的游戏逻辑插件");
        Info.Category = TEXT("Gameplay");
        Info.VersionName = TEXT("1.0.0");
        Info.Version = 1;
        Info.bCanContainContent = true;

        // 将 Info 传递给 PluginToolset 的创建函数
        // UPluginToolset::CreatePlugin(Info);
    }

    /** 启用指定插件 */
    static void EnablePlugin(const FString& PluginName)
    {
        // UPluginToolset::SetPluginEnabled(PluginName, true);
    }
};
```

```cpp
// MyPluginManager.cpp
#include "MyPluginManager.h"

// 实现由 PluginToolset 模块的 UPluginToolset 提供
// 此处仅为调用示例
```

## 模块依赖

从 `.uplugin` 的 Plugins 依赖和 Build.cs 中提取：

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | AI 工具集注册表，用于注册和发现工具 |
| `PluginUtils` | 插件操作工具库，提供底层插件创建/查询能力 |

## 维护状态

### 近期更新

```
- 24cd8c64 2026-05-14 更新 PluginToolset 的描述信息
- 71d2c0c9 2026-05-12 为 UPluginToolset 添加插件描述符编辑工具
- 770b7544 2026-05-12 PluginToolset.SetPluginEnabled：对不存在的插件抛出错误
- 8d6d15aa 2026-05-12 更新 CreatePlugin 使用相对插件路径名，同时更新 FPluginT...
- 8af5936e 2026-05-12 [Backout] - CL53534904
```

### 维护评价

**🆕 全新插件** — PluginToolset 创建于 2026-05-12，距今仅数天，正处于初始开发阶段。

- **活跃度**：非常活跃，创建后连续 3 天有 5 次提交
- **稳定性**：尚不稳定，存在 backout commit（`8af5936e`），说明仍在快速迭代和修正中
- **实验性**：`IsExperimentalVersion=true` 且位于 `Experimental` 目录下
- **功能完整度**：核心功能（列表、检查、创建、启禁用）已基本实现，但 API 可能会变动
- **推荐度**：适合对 AI 辅助开发管线感兴趣的研究者和早期尝鲜者。**不建议**在生产项目中使用，API 随时可能变化。

> ⚠️ 该插件仅数天历史，处于非常早期的实验阶段。请关注后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/PluginToolset)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现测试文件）