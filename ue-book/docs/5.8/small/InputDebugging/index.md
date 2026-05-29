# Input Debugging

> Input debugging and visualization.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 输入调试 |
| 分类 | Input |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InputDebugging` (Runtime), `InputDebuggingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-05-19 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InputDebugging) | |

## 用途

本插件提供了一套输入调试工具，主要用于开发和测试阶段。其核心功能是**触摸输入的实时可视化**。通过控制台命令（如 `Input.Debug.ShowTouches 1`）启用后，可以在游戏视口或编辑器视口中实时绘制出当前的触摸点、轨迹或手势状态，帮助开发者快速定位触摸交互的问题（如触控区域不准确、多点触控冲突等）。

## 使用场景

- 你在开发或测试一个手游，需要实时查看玩家的触摸点和滑动轨迹是否符合预期 → 启用本插件的触摸可视化。
- 你在调试一个复杂的UI界面或多点触控手势（如捏合缩放），需要直观看到每个触摸点的坐标和状态 → 使用本插件。

## 蓝图用法

该插件主要通过控制台命令进行控制，未暴露公开的蓝图可调用节点。

### 核心命令

| 命令 | 说明 | 所在类 |
|---|---|---|
| `Input.Debug.ShowTouches [0/1]` | 开关触摸输入可视化。`1`为开启，`0`为关闭。 | 控制台命令 |

## C++ 用法

本插件主要作为运行时调试工具使用，通常不直接在游戏逻辑的C++代码中调用。其核心功能通过控制台命令系统触发。

### 头文件引入

对于插件的模块本身，使用前需要确保模块依赖正确。对于使用者，通常无需直接包含其头文件。

### 基本用法

在开发版本中，通过控制台命令启用触摸可视化。

```cpp
// 在代码中执行控制台命令（例如，在某个调试函数里）
GEngine->Exec(GetWorld(), TEXT("Input.Debug.ShowTouches 1"));
```

### 进阶用法

插件的`InputDebugging`模块在引擎初始化时注册相关功能和控制台命令。

```cpp
// 参考自 InputDebugging 模块的注册逻辑
// 该插件通过 FCoreDelegates::OnPostEngineInit 等委托与引擎集成
// 开发者通常无需直接操作，插件加载后即可使用其控制台命令
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `ee8a6c98` | Fix touch input debug circle position in editor by offsetting the drawn circle by the game viewport' | 修复了编辑器中触摸调试圆圈的显示位置偏移问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移到 `UE_LOGF`。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了错误的查找替换后的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了之前的某个变更。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复因 `FCoreDelegates` 接口变更导致的初始化注册问题。 |

### 维护评价

该插件创建于约4年前，**近期仍保持活跃维护**（最近一次更新在2026年4月）。更新内容集中在修复可视化位置、适配引擎内部API变更（如日志和委托系统）以及错误修复。作为Epic Games官方维护的调试工具，其稳定性和与引擎版本的同步有保障。对于需要进行触摸输入调试的项目，推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InputDebugging)