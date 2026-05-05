# Batch Renamer

> Rename multiple selected actors or assets, and standardize their prefixes and suffixes.

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AdvancedRenamer` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AdvancedRenamer) | |

## 用途

AdvancedRenamer 是一个**编辑器内批量重命名工具**，提供一个模态对话框面板，让你一次性对多个 Actor 或 Asset 执行复杂的重命名操作。它解决的核心问题是：当你选中了大量对象（比如场景中 100 个灯光 Actor，或者 Content Browser 中一批材质资产），需要统一修改它们的命名规范（加前缀、去后缀、编号、搜索替换等），逐个手动重命名既慢又容易出错。

与引擎自带的单个重命名（F2）不同，AdvancedRenamer 支持**链式操作**——你可以同时启用搜索替换 + 编号 + 大小写转换等多个 Section，它们会按顺序依次作用于每个对象名，形成一个流水线式的重命名管线。它还提供实时预览，在 Apply 之前就能看到所有对象的新旧名字对比。

## 使用场景

- 你选中了场景里的一批 Actor（比如 `Light_01`, `Light_02`, `Cube`），想统一加上 `Env_` 前缀 → 右键 → "Rename Selected Actors" → 打开 Batch Renamer
- 你在 Content Browser 中选中了 50 个纹理资产，想把它们从 `T_` 前缀改为 `Tex_` 前缀 → 右键 → "Batch Rename" → 搜索替换 `T_` → `Tex_`
- 你需要把一批 Actor 按它们在 World Outliner 中的顺序重新编号（如 `Wall_001`, `Wall_002`, ...）→ 使用 Numbering Section
- 你想把一批资产名从 camelCase 统一转为 PascalCase → 使用 Change Case Section
- 你需要先去掉旧后缀 `_v2`，再加新前缀 `NEW_`，同时重新编号 → 同时启用 Remove Suffix + Add Prefix + Numbering 三个 Section

## 编辑器用法

### 入口方式

**方式 1：关卡编辑器（Actor 重命名）**
1. 在 Viewport 或 World Outliner 中选中一个或多个 Actor
2. 右键 → Edit 子菜单 → **"Rename Selected Actors"** 或 **"Rename Actors of Selected Actor Classes"**
3. 模态窗口弹出，显示预览列表和操作面板

**方式 2：Content Browser（资产重命名）**
1. 在 Content Browser 中选中一个或多个资产
2. 右键 → **"Batch Rename"**（位于 Rename 菜单项之后）
3. 模态窗口弹出

**"Rename Selected Actors" vs "Rename Actors of Selected Actor Classes"**：
- **Rename Selected Actors**：只重命名当前选中的 Actor
- **Rename Actors of Selected Actor Classes**：会自动扩展选区，找出当前 World 中所有与选中 Actor **同类**的 Actor 一起重命名。例如你选了 2 个 `PointLight`，它会把世界里所有 `PointLight` 都纳入重命名范围

### 面板结构

打开后是一个模态窗口（最小尺寸 730×589），包含：

1. **预览列表**（上半部分）：表格显示 Original Name 和 New Name，支持拖拽排序
2. **操作 Section**（下半部分）：可叠加的重命名操作面板
3. **按钮栏**：Apply（执行重命名）、Reset（重置所有 Section）、Cancel（取消）

### 内置操作 Section

| Section | 功能 | 选项 |
|---|---|---|
| **Search and Replace** | 搜索并替换名称中的文本 | 支持纯文本 / 正则表达式；可切换大小写敏感/忽略 |
| **Remove Prefix** | 移除名称前缀 | 按分隔符拆分移除 / 按字符数移除 |
| **Remove Suffix** | 移除名称后缀 | 按分隔符拆分移除 / 按字符数移除；可额外移除尾部数字 |
| **Add Prefix/Suffix** | 添加前缀和后缀 | 可分别设置前缀和后缀文本 |
| **Numbering** | 为名称添加编号或字母序号 | 数字模式：起始值 + 步长 + 格式（如 `01`, `001`）；字母模式：起始字母；支持基于预览排序顺序编号 |
| **Change Case** | 修改名称大小写 | Swap First（首字母大写）、Swap All（每个单词首字母大写）、All Lower（全小写）、All Upper（全大写） |

每个 Section 独立运作，但会按顺序链式执行：Search and Replace → Remove Prefix → Remove Suffix → Add Prefix/Suffix → Numbering → Change Case。

## 蓝图用法

AdvancedRenamer 是纯编辑器模块，**没有暴露 BlueprintCallable 节点**。所有功能通过编辑器 UI 或 C++ API 使用。

## C++ 用法

### 头文件引入

```cpp
#include "IAdvancedRenamerModule.h"
#include "Providers/IAdvancedRenamerProvider.h"
```

### 基本用法

**打开 Actor 重命名面板**（来源：`AdvancedRenamerModule.cpp`）

```cpp
// 获取模块引用
IAdvancedRenamerModule& Module = IAdvancedRenamerModule::Get();

// 方式 1：传入 Actor 数组，自动创建 ActorProvider
TArray<AActor*> SelectedActors = /* ... */;
Module.OpenAdvancedRenamerForActors(SelectedActors, ToolkitHost);

// 方式 2：传入自定义 Provider
TSharedRef<IAdvancedRenamerProvider> MyProvider = /* ... */;
Module.OpenAdvancedRenamer(MyProvider, ToolkitHost);

// 方式 3：直接传入已构建好的 IAdvancedRenamer
TSharedRef<IAdvancedRenamer> Renamer = Module.CreateAdvancedRenamer(MyProvider);
// 对 Renamer 做额外配置...
Module.OpenAdvancedRenamer(Renamer, ToolkitHost);
```

### Provider 接口

`IAdvancedRenamerProvider` 是核心抽象接口，定义了重命名操作的生命周期（来源：`Providers/IAdvancedRenamerProvider.h`）：

```cpp
class IAdvancedRenamerProvider
{
public:
    virtual int32 Num() const = 0;                          // 待重命名对象数量
    virtual bool IsValidIndex(int32 InIndex) const = 0;     // 索引是否有效
    virtual uint32 GetHash(int32 InIndex) const = 0;        // 对象唯一标识
    virtual FString GetOriginalName(int32 InIndex) const = 0; // 原始名称
    virtual bool RemoveIndex(int32 InIndex) = 0;            // 从列表移除
    virtual bool CanRename(int32 InIndex) const = 0;        // 是否可重命名

    // 重命名生命周期（Execute 时由 IAdvancedRenamer 调用）
    virtual bool BeginRename() = 0;                                    // 准备阶段
    virtual bool PrepareRename(int32 InIndex, const FString& InNewName) = 0; // 逐项准备
    virtual bool ExecuteRename() = 0;                                  // 批量执行
    virtual bool EndRename() = 0;                                      // 清理阶段
};
```

引擎内置了三种 Provider：

| Provider | 目标类型 | 用途 |
|---|---|---|
| `FAdvancedRenamerActorProvider` | `AActor*` | 重命名关卡中的 Actor |
| `FAdvancedRenamerAssetProvider` | `FAssetData` | 重命名 Content Browser 中的资产 |
| `FAdvancedRenamerObjectProvider` | `UObject*` | 重命名任意 UObject |

### 进阶用法

**筛选 Actor**（来源：`IAdvancedRenamerModule.h`）

模块暴露了一个多播委托，允许你在 Actor 进入重命名面板之前过滤它们：

```cpp
IAdvancedRenamerModule& Module = IAdvancedRenamerModule::Get();

Module.OnFilterAdvancedRenamerActors().AddLambda(
    [](TArray<TWeakObjectPtr<AActor>>& Actors)
    {
        // 移除所有 StaticMeshActor
        Actors.RemoveAll([](const TWeakObjectPtr<AActor>& Actor)
        {
            return Actor.IsValid() && Actor->IsA<AStaticMeshActor>();
        });
    }
);
```

**获取同类型 Actor**（来源：`AdvancedRenamerModule.cpp`）

```cpp
// 给定选中的 Actor，返回当前 World 中所有同类 Actor
TArray<AActor*> AllSameClass = Module.GetActorsSharingClassesInWorld(SelectedActors);
```

该方法会智能处理继承关系：如果选中的 Actor 包含 `AActor` 基类本身，则匹配世界中所有 Actor；否则只匹配非派生的叶子类。

## 架构概览

```
IAdvancedRenamerModule          ← 模块公共接口
  └─ FAdvancedRenamerModule     ← 模块实现
       ├─ FAdvancedRenamer      ← 核心重命名器（持有 Provider + Sections）
       ├─ IAdvancedRenamerProvider ← 数据源抽象接口
       │    ├─ FAdvancedRenamerActorProvider   ← Actor 数据源
       │    ├─ FAdvancedRenamerAssetProvider   ← Asset 数据源
       │    └─ FAdvancedRenamerObjectProvider  ← UObject 数据源
       ├─ IAdvancedRenamerSection ← Section 抽象接口
       │    └─ FAdvancedRenamerSectionBase ← Section 基类
       │         ├─ SearchAndReplace
       │         ├─ RemovePrefix / RemoveSuffix
       │         ├─ AddPrefixSuffix
       │         ├─ Numbering
       │         └─ ChangeCase
       ├─ SAdvancedRenamerPanel ← Slate UI 面板
       ├─ AdvancedRenamerContentBrowserIntegration ← Content Browser 集成
       └─ AdvancedRenamerLevelEditorIntegration   ← Level Editor 集成
```

**执行流程**：
1. Provider 提供待重命名对象列表（`Num()`, `GetOriginalName()`）
2. `FAdvancedRenamer` 为每个对象创建 `FAdvancedRenamerPreview`（原始名 + 新名）
3. `UpdatePreviews()` 遍历所有 Preview，对每个原始名依次调用所有已注册 Section 的 `OnOperationExecuted` 委托
4. 用户预览结果后点击 Apply
5. `Execute()` 调用 Provider 的 `BeginRename()` → 逐项 `PrepareRename()` → `ExecuteRename()` → `EndRename()`

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和容器（公共依赖） |
| `ContentBrowser` | Content Browser 集成（资产右键菜单） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、World 等） |
| `InputCore` | 输入系统 |
| `LevelEditor` | 关卡编辑器集成（Actor 右键菜单） |
| `Projects` | 插件项目系统 |
| `Slate` | Slate UI 框架 |
| `SlateCore` | Slate 核心类型 |
| `ToolMenus` | 工具菜单注册系统 |
| `UMG` | UMG 控件库 |
| `UnrealEd` | 编辑器工具（资产重命名 API 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-11-14 | `c033e1e` | Add a way to disable opening the advanced renamer for actors that don't support renaming | 新增 `OnFilterAdvancedRenamerActors` 委托，允许外部代码在打开重命名器前过滤不支持重命名的 Actor |
| 2024-10-22 | `cabb7dd` | Fix a few more menus that did not take into consideration bCanBeModified | 修复右键菜单在只读资产/Actor 上仍然显示 Batch Rename 的 bug |
| 2024-09-25 | `7428c89` | [BatchRenamer] numbering should be based on the ordering requested and not always on the initial order | 修复编号功能：现在基于预览列表的排序顺序编号，而不是固定使用初始顺序 |

### 维护评价

- **创建时间**：2024 年 1 月，相对较新的插件
- **更新频率**：2024 年有持续更新（1 月创建，9-11 月有功能性修复和增强）
- **实验性状态**：`IsExperimentalVersion=true`，标记为实验性插件
- **代码质量**：架构清晰，Provider/Section 模式设计良好，易于扩展
- **已知限制**：
  - 纯编辑器插件，不支持运行时使用
  - 没有暴露 BlueprintCallable API
  - 没有自定义注册 Section 的公共 API（`Sections` 数组和 `RegisterDefaultSections` 是 Private 的）
  - 文档 URL 为空，无官方文档
- **推荐使用**：✅ 推荐。虽然是实验性标记，但功能完整且持续维护中。作为编辑器工具使用没有风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AdvancedRenamer)
- 官方文档：无
