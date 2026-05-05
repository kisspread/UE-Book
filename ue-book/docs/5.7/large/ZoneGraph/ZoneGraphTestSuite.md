# ZoneGraphTestSuite — 自动化测试模块

> ZoneGraph 的自动化测试套件。当前为空壳，无实际测试用例。

## 模块概览

| 属性 | 值 |
|---|---|
| 模块名 | `ZoneGraphTestSuite` |
| 类型 | UncookedOnly |
| 加载阶段 | Default |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ZoneGraph/Source/ZoneGraphTestSuite) | |

## 依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | Actor/Component |
| `AIModule` | AI 模块 |
| `ZoneGraph` | ZoneGraph 核心 |
| `AITestSuite` | AI 测试框架 |

## 现状

`ZoneGraphTest.cpp` 当前只有空的 LOCTEXT 宏定义，**没有实际测试用例**。模块框架已搭建（依赖 AITestSuite），但 Epic 尚未添加测试。

## 文件列表

| 文件 | 说明 |
|---|---|
| `ZoneGraphTest.cpp` | 测试文件（当前为空） |
| `ZoneGraphTestSuite.cpp` | 模块注册 |
| `ZoneGraphTestSuite.h` | 模块头文件 |
