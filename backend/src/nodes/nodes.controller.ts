import { Controller, Get, Put, Body } from '@nestjs/common';
import { NodesService } from './nodes.service';
import { CreateNodeDto } from './dto/create-node.dto';

@Controller('api/v1')
export class NodesController {
    constructor(private readonly nodesService: NodesService) { }

    @Put('nodes')
    async createNode(@Body() nodeData: CreateNodeDto) {
        return await this.nodesService.createOrUpdateNode(nodeData);
    }

    @Get('graph')
    async getGraph() {
        return await this.nodesService.getGraph();
    }
}
