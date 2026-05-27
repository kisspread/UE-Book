# Submit Tool Editor Override

> Sets up Submit Tool to be launched by the editor（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 提交工具编辑器覆盖 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SubmitToolEditor` (Editor) |
| 实验性 | ⚥️ 是 |
| 创建时间 | 2025-01-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SubmitToolEditor) | |

## 用途

此插件覆盖 UE 编辑器内置的源代码控制（Source Control）提交流程。当用户在编辑器中触发提交操作时，标准的提交对话框被替换为调用外部自定义提交工具（Submit Tool）。

这个插件存在的意义是为团队提供一种将自定义提交工具（如集成代码审查系统、自定义校验流程、专用提交 UI 等）接入编辑器源码控制管线的方式。插件会拦截编辑器的提交委托，在提交前执行数据校验（Data Validation），并根据校验结果向提交工具传递自定义标签和参数。

核心流程：
1. 注册源代码控制模块的提交覆盖委托（Submit Override Delegate）
2. 拦截提交操作，调用外部提交工具进程
3. 可选：在调用提交工具前执行数据校验，根据校验结果更新 changelist 描述中的标签或附加参数
4. 支持 Perforce provider 的特殊参数获取（端口、用户、客户端、工作空间路径）

## 使用场景

- 你的团队使用自定义提交工具（如内部代码审查/CI 集成工具）替代编辑器默认提交流程 → 启用此插件并将 SubmitToolPath 指向你的工具
- 你需要在提交前强制执行数据校验，并将校验结果以标签形式写入 changelist 描述 → 配置 `bEnforceDataValidation` 和 `ChangelistTagTriggers`
- 你需要根据校验消息动态向提交工具传递不同参数 → 配置 `OptionalArgumentTriggers`
- 你使用 Perforce 作为源码控制，需要自动获取 port/user/client 等信息传递给外部工具

## 蓝图用法

此插件没有暴露 BlueprintCallable 函数。所有配置通过编辑器的 **Project Settings → Submit Tool Settings** 界面完成。

### 配置项（Project Settings）

| 设置项 | 类型 | 说明 |
|---|---|---|
| `SubmitToolPath` | FString | 外部提交工具的可执行文件路径 |
| `SubmitToolArguments` | FString | 传递给提交工具的命令行参数 |
| `bSubmitToolEnabled` | bool | 是否启用提交工具覆盖 |
| `bForceSubmitTool` | bool | 是否强制使用提交工具（默认 true） |
| `bEnforceDataValidation` | bool | 是否在提交前强制执行数据校验 |
| `ChangelistTagTriggers` | TArray | 根据校验消息正则匹配自动添加 changelist 标签 |
| `OptionalArgumentTriggers` | TArray | 根据校验消息正则匹配自动追加提交工具参数 |

### 触发器配置说明

**ChangelistTagTrigger**：当校验消息匹配 `RegExMessage` 时，将 `SubmitToolTag` 追加到 changelist 描述中。

**ArgumentTrigger**：当校验消息匹配 `RegExMessage` 时，将 `SubmitToolArgument` 作为额外参数传递给提交工具。

## C++ 用法

此插件主要通过配置驱动，C++ 层面主要用于模块注册和内部委托处理。

### 头文件引入

```cpp
#include "SubmitToolEditor.h"
```

### 基本用法 — 获取模块实例

```cpp
// 获取 SubmitToolEditor 模块的单例引用
FSubmitToolEditorModule& SubmitToolModule = FSubmitToolEditorModule::Get();
```

### 注册/注销提交覆盖

```cpp
// 根据设置注册提交覆盖委托
const USubmitToolEditorSettings* Settings = GetDefault<USubmitToolEditorSettings>();
FSubmitToolEditorModule::Get().RegisterSubmitOverrideDelegate(Settings);

// 注销提交覆盖委托
FSubmitToolEditorModule::Get().UnregisterSubmitOverrideDelegate();
```

### 注意事项

- 模块类型为 `Editor`，仅在编辑器环境下可用，不会被打包到运行时构建中
- `EnabledByDefault` 为 false，需要在 `.uproject` 或编辑器插件列表中手动启用
- 插件内部维护了 `FProcHandle` 用于管理外部提交工具进程的生命周期

## Demo 示例

此插件无需编写 C++ 代码即可使用。配置步骤如下：

1. 在编辑器中启用插件：**Edit → Plugins → 搜索 "Submit Tool Editor Override" → 启用**
2. 重启编辑器
3. 打开 **Edit → Project Settings → 搜索 "Submit Tool Settings"**
4. 配置提交工具路径和参数：
   - **Submit Tool Path**: `/path/to/your/submit_tool.exe`
   - **Submit Tool Arguments**: `--arg1 --arg2`
   - **Submit Tool Enabled**: ✅
   - **Enforce Data Validation**: 根据需要开启
5. 如需根据校验结果自动添加标签，配置 **Changelist Tag Triggers**
6. 如需根据校验结果动态附加参数，配置 **Optional Argument Triggers**

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SourceControl` | 访问源代码控制 Provider、注册提交验证委托、操作 changelist |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏（编译改进） |
| 2025-11-25 | `c0ee383c` | Fix new changelist created in editor not running data validation before invoking submit tool | 修复新建 changelist 时未在调用提交工具前执行数据校验的 bug |
| 2025-11-11 | `64968397` | Add validation message parsing to SubmitToolEditor. | 新增对校验消息的解析功能 |
| 2025-11-03 | `a757ea03` | Modify ISourceControlModule submit validation delegates. | 修改源码控制模块的提交验证委托接口 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加内联生成宏（编译优化） |

### 维护评价

- **年龄**：约 1 年的实验性插件
- **更新频率**：2025 年 11 月有密集的功能性更新（校验解析、bug 修复），2026 年 4 月有编译适配更新
- **维护状态**：活跃维护中，仍在持续改进
- **已知限制**：
  - 实验性插件（`IsExperimentalVersion=true`），API 可能变动
  - 默认未启用（`EnabledByDefault=false`），需手动开启
  - 源码文件较少（4 个），功能相对聚焦
- **推荐程度**：如果你的团队需要在 UE 编辑器中集成自定义提交工具，推荐使用。注意这是实验性功能，生产环境使用需关注后续版本变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SubmitToolEditor)
- 官方文档：无