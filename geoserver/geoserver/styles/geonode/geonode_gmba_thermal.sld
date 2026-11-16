<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>GMBA-THERMAL</sld:Name>
    <sld:UserStyle>
      <sld:Name>GMBA-THERMAL</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:Geometry>
              <ogc:PropertyName>grid</ogc:PropertyName>
            </sld:Geometry>
            <sld:ColorMap type="values">
               <sld:ColorMapEntry color="#FFFFFF" opacity="0" quantity="0" label=""/>
              <sld:ColorMapEntry color="#74abad" opacity="1.0" quantity="1" label="&lt; 3.5 C GS &lt; 10 days"/>
              <sld:ColorMapEntry color="#acc993" opacity="1.0" quantity="2" label="&lt; 3.5 C, GS &lt; 94 days"/>
              <sld:ColorMapEntry color="#e3eb75" opacity="1.0" quantity="3" label="&lt; 6.4 C, GS &lt; 54days"/>
              <sld:ColorMapEntry color="#fcde56" opacity="1.0" quantity="4" label="&gt; 6.4 C &lt; 0 C"/>
              <sld:ColorMapEntry color="#fca03d" opacity="1.0" quantity="5" label="&gt; 10 C &gt;=15 C"/>
              <sld:ColorMapEntry color="#f57b25" opacity="1.0" quantity="6" label="&gt; 15 C with frost"/>
              <sld:ColorMapEntry color="#f55925" opacity="1.0" quantity="7" label="&gt; 15 C without frost"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>