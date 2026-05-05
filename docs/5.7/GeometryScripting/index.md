# Geometry Script

> Geometry Script provides a library of functions for creating and editing Meshes in Blueprints and Python

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（函数库、示例资产） |
| 模块 | `GeometryScriptingCore` (Runtime), `GeometryScriptingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-09-12 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting) | |

## 用途

Geometry Script 是一个功能强大的运行时几何操作函数库。它解决了在蓝图和 Python 脚本中程序化创建和编辑静态网格体（Static Mesh）的难题。传统上，这类操作需要编写复杂的 C++ 代码或依赖编辑器手动操作，而 Geometry Script 将这些底层几何处理算法封装成了易于调用的蓝图节点和 Python 函数，极大地提升了程序化内容生成（PCG）和自动化资产处理的工作流效率。

## 使用场景

- **程序化生成**：在蓝图或 Python 中动态生成地形、建筑、道具等复杂几何体。
- **资产批处理**：自动化执行网格体的清理、简化、UV 重映射、法线计算等后处理流程。
- **快速原型设计**：无需离开编辑器或编写 C++，即可通过脚本快速测试几何体修改想法。
- **游戏逻辑驱动的几何变形**：根据游戏状态（如破坏、生长）实时修改网格体。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `GeometryScriptingCore` | Runtime | 核心运行时模块，包含所有几何操作函数库，可在游戏和编辑器中使用。 |
| `GeometryScriptingEditor` | Editor | 编辑器扩展模块，提供资产处理工具、编辑器内蓝图调试支持等。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/GeometryScriptingTests)